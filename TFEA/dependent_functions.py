#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This file contains a list of dependent functions that rely on other 
    functions to work properly
'''
#==============================================================================
__author__ = 'Jonathan D. Rubin and Rutendo Sigauke'
__credits__ = ['Jonathan D. Rubin', 'Rutendo Sigauke', 'Jacob Stanley', 
                'Robin Dowell']
__maintainer__ = 'Jonathan D. Rubin'
__email__ = 'Jonathan.Rubin@colorado.edu'
#==============================================================================
import matplotlib
matplotlib.use('Agg')
import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
from matplotlib import gridspec
from scipy.stats import norm 
import time
import config
import independent_functions
#==============================================================================
#Functions
#==============================================================================
def deseq_run(tempdir=config.TEMPDIR):
    '''Writes the DE-Seq script, runs the DE-Seq script, and plots the DE-Seq 
        MA plot

    Parameters
    ----------
    tempdir : string
        full path to temp directory in output directory (created by TFEA)

    Returns
    ----------
    None
    '''
    independent_functions.write_deseq_script()
    os.system("R < " + tempdir + "DESeq.R --no-save")
    independent_functions.plot_deseq_MA(tempdir+'DESeq.res.txt')
#==============================================================================

#==============================================================================
def calculate_es_auc(args, fimo=config.FIMO, 
                        ranked_center_file=config.RANKED_CENTER_FILE,
                        motif_hits=config.MOTIF_HITS, plot=config.PLOT,
                        padj_cutoff=config.PADJCUTOFF, logos=config.LOGOS,
                        figuredir=config.FIGUREDIR,
                        largewindow=config.LARGEWINDOW,
                        smallwindow=config.SMALLWINDOW,gc_array=list()):
    '''This function calculates the AUC for any TF based on the TF motif hits 
        relative to the bidirectionals. The calculated AUC is used as a proxy 
        for the enrichemnt of the TFs.

    Parameters
    ----------
    args : tuple 
        contains two arguments that are unpacked within this function:
            motif_file : string
                the name of a motif bed file contained within MOTIF_HITS
            millions_mapped : list or array
                contiains a list of floats that corresponds to the millions 
                mapped reads for each bam file

    Returns
    -------
    AUC : float
        the area under the curve (AUC) for a given tf

    p-value : float
        theoretical p-value calculated by comparing the observed value  to the
        distribution of all simulations (default:1000)
                 
    Raises
    ------
    ValueError
        when tf does not have any hits
    '''
    motif_file, millions_mapped = args
    if fimo:
        ranked_fullregions_file = independent_functions.get_regions()
        ranked_fasta_file = independent_functions.getfasta(
                                bedfile=ranked_fullregions_file)

        background_file = independent_functions.get_bgfile(
                                fastafile=ranked_fasta_file)

        fimo_file = independent_functions.fimo(background_file, motif_file,
                                                ranked_fasta_file)

        independent_functions.meme2images(motif_file)
        ranked_center_distance_file = independent_functions.fimo_distance(
                                                                    fimo_file,
                                                                    motif_file)
    else:
        ranked_center_distance_file = \
            independent_functions.motif_distance_bedtools_closest(
                                                        ranked_center_file,
                                                        motif_hits+motif_file)

    distances = []
    ranks = []
    pvals= []
    pos = 0
    fc = []

    with open(ranked_center_distance_file) as F:
        for line in F:
            line = line.strip('\n').split('\t')
            distance = int(line[-1])
            rank = int(line[5])
            pvals.append(float(line[3]))
            fc.append(float(line[4]))
            ranks.append(rank)
            distances.append(distance)
            if distance < largewindow:
                pos+=1

    #sort distances based on the ranks from TF bed file
    #and calculate the absolute distance
    sorted_distances = [x for _,x in sorted(zip(ranks, distances))]
    distances_abs = [abs(x) for x in sorted_distances] 

    #filter any TFs/files without and hits
    if len(distances_abs) == 0:
        return "no hits"

    #Get -exp() of distance and get cumulative scores
    score = [math.exp(-x) for x in distances_abs] 
    total = float(sum(score))
    normalized_score = [x/total for x in score]
    cumscore = np.cumsum(normalized_score)

    #The AUC is the relative to the "random" line
    actualES = np.trapz(cumscore) - (0.5*len(cumscore))

    #Calculate random AUC
    simES = independent_functions.permutations(normalized_score)

    ##significance calculator                                                                                                                                                            
    mu = np.mean(simES)
    NES = actualES/abs(mu)
    sigma = np.std(simES)


    if actualES > 0:
        p = 1-norm.cdf(actualES,mu,sigma)
    else:
        p = norm.cdf(actualES,mu,sigma)

    plot_individual_graphs(distances_abs=distances_abs, 
                            sorted_distances=sorted_distances,ranks=ranks,
                            pvals=pvals, fc=fc, cumscore=cumscore, 
                            motif_file=motif_file, p=p, simES=simES, 
                            actualES=actualES, gc_array=gc_array)

    return [motif_file.split('.bed')[0],actualES,NES,p,pos]
#==============================================================================

#==============================================================================
def plot_individual_graphs(plot=config.PLOT, padj_cutoff=config.PADJCUTOFF,
                            figuredir=config.FIGUREDIR, logos=config.LOGOS, 
                            largewindow=config.LARGEWINDOW, 
                            smallwindow=config.SMALLWINDOW,
                            distances_abs=list(), sorted_distances=list(),
                            ranks=list(),pvals=list(),fc=list(), 
                            cumscore=list(), motif_file='',p=float(),
                            simES=float(), actualES=float(), gc_array=list()):

    #Only plot things if user selects to plot all or if the pvalue is less than
    #the cutoff
    if plot or p < padj_cutoff:

        #Filter distances into quartiles for plotting purposes
        q1 = round(np.percentile(np.arange(1, len(distances_abs),1), 25))
        q3 = round(np.percentile(np.arange(1, len(distances_abs),1), 75))
        updistancehist = distances_abs[0:int(q1)]
        middledistancehist =  distances_abs[int(q1):int(q3)]
        downdistancehist = distances_abs[int(q3):len(distances_abs)]

        
        #Get log pval to plot for rank metric
        sorted_pval = [x for _,x in sorted(zip(ranks, pvals))]
        sorted_fc = [x for _,x in sorted(zip(ranks, fc))]
        try:
            logpval = [math.log(x,10) if y < 1 else -math.log(x,10) \
                        for x,y in zip(sorted_pval,sorted_fc)]
        except ValueError:
            logpval = sorted_pval

        #Plot results for significant hits while list of simulated ES scores is
        #in memory                              
        if 'HO_' in motif_file:
            os.system("scp " + logos 
                        + motif_file.split('.bed')[0].split('HO_')[1] 
                        + "_direct.png " + figuredir)

            os.system("scp " + logos 
                        + motif_file.split('.bed')[0].split('HO_')[1] 
                        + "_revcomp.png " + figuredir)
        else:
            os.system("scp " + logos + motif_file.split('.bed')[0] 
                        + "_direct.png " + figuredir)

            os.system("scp " + logos + motif_file.split('.bed')[0] 
                        + "_revcomp.png " + figuredir)


        #Begin plotting section
        F = plt.figure(figsize=(15.5,8))
        xvals = range(1,len(cumscore)+1)
        limits = [1,len(cumscore)]
        gs = gridspec.GridSpec(4, 1, height_ratios=[2, 2, 1, 1])

        #This is the enrichment score plot (i.e. line plot)
        ax0 = plt.subplot(gs[0])
        ax0.plot(xvals,cumscore,color='green')
        ax0.plot([0, len(cumscore)],[0, 1], '--', alpha=0.75)
        ax0.set_title('Enrichment Plot: ',fontsize=14)
        ax0.set_ylabel('Enrichment Score (ES)', fontsize=10)
        ax0.tick_params(axis='y', which='both', left='on', right='off', 
                        labelleft='on')
        ax0.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='off')
        ylims = ax0.get_ylim()
        ymax = math.fabs(max(ylims,key=abs))
        ax0.set_ylim([0,ymax])
        ax0.set_xlim(limits)

        #This is the distance scatter plot right below the enrichment score 
        #plot
        ax1 = plt.subplot(gs[1])
        ax1.scatter(xvals,sorted_distances,edgecolor="",color="black",s=10,
                    alpha=0.25)
        ax1.tick_params(axis='y', which='both', left='off', right='off', 
                        labelleft='on')
        ax1.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='off')
        ax1.set_xlim(limits)
        ax1.set_ylim([-int(largewindow),int(largewindow)])
        plt.yticks([-int(largewindow),0,int(largewindow)],
                    [str(-int(largewindow)/1000.0),'0',\
                    str(int(largewindow)/1000.0)])
        ax1.set_ylabel('Distance (kb)', fontsize=10)

        #This is the rank metric plot
        ax2 = plt.subplot(gs[3])
        ax2.fill_between(xvals,0,logpval,facecolor='grey',edgecolor="")
        ax2.tick_params(axis='y', which='both', left='on', right='off', 
                        labelleft='on')
        ax2.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='on')
        ylim = math.fabs(max([x for x in logpval if -500 < x < 500],key=abs))
        ax2.set_ylim([-ylim,ylim])
        ax2.yaxis.set_ticks([int(-ylim),0,int(ylim)])
        ax2.set_xlim(limits)
        ax2.set_xlabel('Rank in Ordered Dataset', fontsize=14)
        ax2.set_ylabel('Rank Metric',fontsize=10)
        try:
            ax2.axvline(len(updistancehist)+1,color='green',alpha=0.25)
        except ValueError:
            pass
        try:
            ax2.axvline(len(xvals) - len(downdistancehist), color='purple', 
                        alpha=0.25)
        except ValueError:
            pass

        #This is the GC content plot
        ax3 = plt.subplot(gs[2])
        ax3.set_xlim(limits)
        GC_ARRAY = np.array(gc_array).transpose()
        sns.heatmap(GC_ARRAY, cbar=False, xticklabels='auto',
                    yticklabels='auto')

        plt.yticks([0,int(largewindow),int(largewindow*2)],
                    [str(-int(largewindow)/1000.0),'0',\
                    str(int(largewindow)/1000.0)])

        ax3.tick_params(axis='y', which='both', left='on', right='off', 
                        labelleft='on')

        ax3.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='off')

        ax3.set_ylabel('GC content per kb',fontsize=10)

        plt.savefig(figuredir + motif_file.split('.bed')[0] 
                    + '_enrichment_plot.png',bbox_inches='tight')

        plt.cla()

        F = plt.figure(figsize=(7,6))
        ax2 = plt.subplot(111)
        maximum = max(simES)
        minimum = min(simES)
        ax2.hist(simES,bins=100)
        width = (maximum-minimum)/100.0
        rect = ax2.bar(actualES,ax2.get_ylim()[1],color='red',width=width*2)[0]
        height = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2., 1.05*height, 
                    'Observed ES', ha='center', va='bottom')

        ax2.set_xlim([min(minimum,actualES)-(width*40), \
                    max(maximum,actualES)+(width*40)])

        ax2.set_ylim([0,(1.05*height)+5])
        ax2.tick_params(axis='y', which='both', left='off', right='off', 
                        labelleft='on')

        ax2.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='on')

        plt.title('Distribution of Simulated Enrichment Scores',fontsize=14)
        ax2.set_ylabel('Number of Simulations',fontsize=14)
        ax2.set_xlabel('Enrichment Score (ES)',fontsize=14)
        plt.savefig(figuredir + motif_file.split('.bed')[0] 
                    + '_simulation_plot.png',bbox_inches='tight')

        plt.cla()


        #Plots the distribution of motif distances with a red line at h                                                                                                                                                                   
        F = plt.figure(figsize=(6.5,6))
        gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
        ax0 = plt.subplot(gs[0])
        binwidth = largewindow/100.0
        ax0.hist(updistancehist,
                    bins=np.arange(0,int(largewindow)+binwidth,binwidth),
                    color='green')
        ax0.set_title('Distribution of Motif Distance for: fc > 1',fontsize=14)
        ax0.axvline(smallwindow,color='red',alpha=0.5)
        ax0.tick_params(axis='y', which='both', left='off', right='off', 
                        labelleft='on')
        ax0.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='off')
        ax0.set_xlim([0,largewindow])
        ax0.set_ylabel('Hits',fontsize=14)
        ax1 = plt.subplot(gs[2])
        ax1.hist(downdistancehist,
                    bins=np.arange(0,int(largewindow)+binwidth,binwidth),
                    color='purple')

        ax1.axvline(smallwindow,color='red',alpha=0.5)
        ax1.set_title('Distribution of Motif Distance for: fc < 1',fontsize=14)
        ax1.tick_params(axis='y', which='both', left='off', right='off', 
                        labelleft='on')

        ax1.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='on')

        ax1.set_xlim([0,largewindow])
        ax1.set_ylabel('Hits',fontsize=14)
        ax1.set_xlabel('Distance (bp)',fontsize=14)
        ax2 = plt.subplot(gs[1])
        ax2.hist(middledistancehist,
                    bins=np.arange(0,int(largewindow)+binwidth,binwidth),
                    color='blue')

        ax2.set_title('Distribution of Motif Distance for: middle',fontsize=14)
        ax2.axvline(smallwindow,color='red',alpha=0.5)
        ax2.tick_params(axis='y', which='both', left='off', right='off', 
                        labelleft='on')
        ax2.tick_params(axis='x', which='both', bottom='off', top='off', 
                        labelbottom='off')
        ax2.set_xlim([0,largewindow])
        ax2.set_ylabel('Hits',fontsize=14)
        plt.savefig(figuredir + motif_file.split('.bed')[0] 
                    + '_distance_distribution.png',bbox_inches='tight')                                                                                                             
        plt.cla()
#==============================================================================

#==============================================================================
def plot_global_graphs(padj_cutoff=config.PADJCUTOFF, label1=config.LABEL1,
                        label2=config.LABEL2, figuredir=config.FIGUREDIR, 
                        TFresults=list()):
    '''This function plots graphs that are displayed on the main results.html 
        filethat correspond to results relating to all analyzed TFs.

    Parameters
    ----------
    TFresults : list of lists
        contains calculated enrichment scores for all TFs of interest specified
        by the user
        
    Returns
    -------
    TFresults : list of lists
        same as input with an additional p-adjusted value appended to each TF
    '''
    TFresults = independent_functions.padj_bonferroni(TFresults=TFresults)

    ESlist = [i[1] for i in TFresults]
    NESlist = [i[2] for i in TFresults]
    PVALlist = [i[3] for i in TFresults]
    POSlist = [math.log(i[4],10) if i[4] != 0 else 0 for i in TFresults]
    PADJlist = [i[5] for i in TFresults]

    sigx = [x for x, p in zip(ESlist, PADJlist) if p < padj_cutoff]
    sigy = [p for x, p in zip(ESlist, PADJlist) if p < padj_cutoff]

    MAy = sigx
    MAx = [x for x, p in zip(POSlist, PADJlist) if p < padj_cutoff]

    #Creates a moustache plot of the global PADJs vs. ESs                                                                                                                                                                                       
    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    ax.scatter(ESlist,PADJlist,color='black',edgecolor='')
    ax.scatter(sigx,sigy,color='red',edgecolor='')
    ax.set_title("TFEA Moustache Plot",fontsize=14)
    ax.set_xlabel("Enrichment Score (ES)",fontsize=14)
    ax.set_ylabel("Adjusted p-value (PADJ)",fontsize=14)
    xlimit = math.fabs(max(ESlist,key=abs))
    ylimit = math.fabs(max(PADJlist,key=abs))
    ax.set_xlim([-xlimit,xlimit])
    ax.set_ylim([0,ylimit])
    ax.tick_params(axis='y', which='both', left='off', right='off', 
                    labelleft='on')

    ax.tick_params(axis='x', which='both', bottom='off', top='off', 
                    labelbottom='on')

    plt.savefig(config.FIGUREDIR + 'TFEA_Results_Moustache_Plot.png',
                    bbox_inches='tight')
    plt.cla()

    #Creates a histogram of p-values                                                                                                                                                                                                            
    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    binwidth = 1.0/100.0
    ax.hist(PVALlist,bins=np.arange(0,0.5+binwidth,binwidth),color='green')
    ax.set_title("TFEA P-value Histogram",fontsize=14)
    ax.set_xlabel("P-value",fontsize=14)
    ax.set_ylabel("Count",fontsize=14)
    ax.tick_params(axis='y', which='both', left='off', right='off', 
                    labelleft='on')

    ax.tick_params(axis='x', which='both', bottom='off', top='off', 
                    labelbottom='on')

    plt.savefig(figuredir + 'TFEA_Pval_Histogram.png',
                    bbox_inches='tight')
    plt.cla()

    #Creates an MA-plot with NES on Y-axis and positive hits on X-axis                                                                                                                                                                                                      
    F = plt.figure(figsize=(7,6))
    ax = plt.subplot(111)
    ax.scatter(POSlist,ESlist,color='black',edgecolor='')
    ax.scatter(MAx,MAy,color='red',edgecolor='')
    ax.set_title("TFEA MA-Plot",fontsize=14)
    ax.set_ylabel("Normalized Enrichment Score (NES) " + label2 + "/" 
                    + label1, fontsize=14)

    ax.set_xlabel("Hits Log10",fontsize=14)
    ax.tick_params(axis='y', which='both', left='off', right='off', 
                    labelleft='on')

    ax.tick_params(axis='x', which='both', bottom='off', top='off', 
                    labelbottom='on')

    plt.savefig(figuredir + 'TFEA_NES_MA_Plot.png',bbox_inches='tight')
    plt.cla()
#==============================================================================

#==============================================================================
def get_gc_array(tempdir=config.TEMPDIR, ranked_file='',
                    window=int(config.LARGEWINDOW),bins=1000):
    '''This function calculates gc content over all eRNAs. It uses the 
    LARGEWINDOW variable within the config file instead of the whole region. 
    It performs a running average of window size = total_regions/bins

    Parameters
    ----------
    ranked_bed_file : str
        full path to a tab delimited bedfile with regions ranked by some metric
        of differential transcription
    window : int
        the size of the window (in bp) that you wish to calculate gc content 
        for
    bins : int 
        the number of equal sized bins to compute for the gc array
        
    Returns
    -------
    final_array : numpy array
        a list of gc content averaged to have bins equal to bins specified in
        paramters
    '''

    #First, create a bed file with the correct coordinates centered on the 
    #given regions with the specified window size on either side
    outfile = open(tempdir+"ranked_file.windowed.bed",'w')
    with open(tempdir + "ranked_file.bed") as F:
        for line in F:
            line = line.strip('\n').split('\t')
            chrom,start,stop = line[:3]
            center = (int(start)+int(stop))/2
            newstart = center - window
            newstop = center + window
            outfile.write(chrom + '\t' + str(newstart) + '\t' + str(newstop) 
                            + '\t' + '\t'.join(line[3:]) + '\n')
    outfile.close()

    #Convert the bed file created above into a fasta file using meme (contained
    #within the combine_bed file for some reason)
    ranked_file_windowed_fasta = independent_functions.getfasta(tempdir
                                                +"ranked_file.windowed.bed")

    #Create a gc_array which simply contains all sequences in fasta file c
    #ollapsed into 1.0 for G/C and 0.0 for A/T
    gc_array = []
    with open(ranked_file_windowed_fasta) as F:
        for line in F:
            if '>' not in line:
                line = line.strip('\n')
                gc_content = independent_functions.convert_sequence_to_array(
                                                                sequence=line)
                gc_array.append(gc_content)

    #The length of each bin is equal to the total positions over the number of 
    #desired bins
    binwidth = len(gc_array)/bins

    #Collapse the gc_array into an array containing the correct number of bins 
    #(specified by user)
    final_array = []
    ##First, step through the gc_array with binwidth step size (i)
    for i in range(0,len(gc_array),binwidth):
        ##Initialize a position_average list that will store the mean value for
        #each position (along the window)
        position_average = []
        ##Now we step through the total window size (window*2) position by 
        #position
        for k in range(window*2):
            ##new_array stores for each position in the window, a binwidth 
            #amount of data points to be averaged
            new_array = []
            ##Now, if we are not at the end of the gc_array, we will step 
            #through for each position, a binwidth amount of values and store 
            #them in new_array
            if i+binwidth < len(gc_array):
                for j in range(i,i+binwidth):
                    new_array.append(gc_array[j][k])
            else:
                for j in range(i,len(gc_array)):
                    new_array.append(gc_array[j][k])
            ##Finally, we simply append the average of the new_array into the 
            #position_average list
            position_average.append(np.mean(new_array))
        ##And this poition_average list is appended to the actual GC_ARRAY 
        #within the config file for later use
        final_array.append(position_average)

    final_array = np.array(final_array).transpose()

    return final_array
#==============================================================================

#==============================================================================
