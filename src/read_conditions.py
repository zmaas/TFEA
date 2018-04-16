__author__ = 'Jonathan Rubin'

import combine_bed
import count_reads
import DESeq

def run(conditions,keyword,specificcelltype,untreated,treated,bamdir,beddir):
    untreatedSRR = list()
    treatedSRR = list()
    with open(conditions) as F:
        for line in F:
            line = line.strip('\n').split(',')
            if keyword == line[8] and specificcelltype == line[4]:
                treatment = line[5]
                if treatment == untreated:
                    untreatedSRR.append(line[0])
                elif treatment == treated:
                    treatedSRR.append(line[0])
                else:
                    pass

    beds = list()
    bam1 = list()
    for SRR in untreatedSRR:
        bam1.append(bamdir+SRR+'.fastqbowtie2.sorted.bam')
        beds.append(beddir+SRR+'-1_bidir_predictions.bed')

    bam2 = list()
    for SRR in treatedSRR:
        bam2.append(bamdir+SRR+'.fastqbowtie2.sorted.bam')
        beds.append(beddir+SRR+'-1_bidir_predictions.bed')

    return bam1,bam2,beds

if __name__ == "__main__":
    CONDITIONS='/scratch/Shares/dowell/pubgro/conditions_short_20161103_tentative.txt_20161107-165140.csv'
    ##SPECIFICCELLTYPE = 'HCT116'
    SPECIFICCELLTYPE = 'MCF7'
    ##SPECIFICCELLTYPE = 'AC16'
    ##LABEL1='DMSO_1hr'
    LABEL1='vehicle'
    ##LABEL1='control_notvechicle'
    ##LABEL2='Nutlin_1hr'
    LABEL2='E2_40min'
    ##LABEL2='TNFa_30min'
    BAMDIR='/scratch/Shares/dowell/pubgro_sortedbams/'
    BEDDIR='/scratch/Shares/dowell/md_score_paper/tfit_bed_files/human/recent/'
    ##KEYWORD='Allen2014'
    KEYWORD='Hah2013'
    ##KEYWORD='Luo2014'
    ##FILEDIR='/scratch/Users/rusi2317/projects/rotation/output/TFEA/Allen2014/'
    FILEDIR='/scratch/Users/rusi2317/projects/rotation/output/TFEA/Hah2013/'
    ##FILEDIR='/scratch/Users/rusi2317/projects/rotation/output/TFEA/Luo2014'
    BAM1,BAM2,BEDS = run(CONDITIONS,KEYWORD,SPECIFICCELLTYPE,LABEL1,LABEL2,BAMDIR,BEDDIR)
    BED = combine_bed.run(BEDS,FILEDIR)
    count_reads.run(BED,BAM1,BAM2,LABEL1,LABEL2,FILEDIR)
    DESeq.write_script(LABEL1,LABEL2,BAM1,BAM2,FILEDIR,FILEDIR)
    DESEQFILE = DESeq.run(LABEL1,LABEL2,BAM1,BAM2,FILEDIR,FILEDIR)



    

    