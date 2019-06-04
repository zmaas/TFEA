<H1>Transcription Factor Enrichment Analysis (TFEA)</H1>
<H2 id="TableOfContents">Table of Contents</H2>

1. <A href="#Pipeline">Pipeline</A>
2. <A href="#InstallationandRequirements">Installation and Requirements</A>
   - <A href="#DESeq">DESeq</A>
   - <A href="#Bedtools">Bedtools</A>
   - <A href="#MEMESuite">MEME Suite</A>
     - <A href="#ImageMagick">Image Magick</A>
   - <A href="#FIJIModules">FIJI Modules</A>
4. <A href="#Usage">Usage</A>
   - <A href="#ConfigurationFile">Configuration File</A>
   - <A href="#UsingSBATCH">Using SBATCH</A>
   - <A href="#PreProcessedInputs">Pre-Processed Inputs</A>
   - <A href="#SecondaryAnalysis">Secondary Analysis (MD, MDD)</A>
   - <A href="#HelpMessage">Help Message</A>
6. <A href="#ExampleOutput">Example Output</A>
7. <A href="#ContactInformation">Contact Information</A>
 
<br></br>
 
<H2 id="Pipeline">TFEA Pipeline</H2>
 
![TFEA Pipeline](https://github.com/jdrubin91/TFEA/blob/master/TFEA_Pipeline2.png)
 
<br></br>

<H2 id="InstallationandRequirements">Installation and Requirements</H2>

To install, this package and all python3 dependencies:

```
git clone https://github.com/jdrubin91/TFEA.git
cd /full/path/to/TFEA/
pip3 install --user .
```

<b>*Note:*</B> If you plan to run TFEA only on FIJI using the --sbatch flag, then you only need to install DESeq and DESeq2. Otherwise, follow the instructions below for installing all TFEA dependencies.

  <H3 id="DESeq">DESeq</H3>
  TFEA uses DESeq or DESeq2 (depending on replicate number) to rank inputted bed files based on fold change significance. If on FIJI, make sure all gcc modules are unloaded before installing DESeq or DESeq2. This can be accomplished with:
  
  ```
  module unload gcc
  ```
  
  or
  
  ```
  module purge
  ```
  
  To install DESeq and DESeq2 type in your terminal:
    
  ```
  R
  
  > if (!requireNamespace("BiocManager", quietly = TRUE))
  >   install.packages("BiocManager")
  
  > BiocManager::install("DESeq")
  > BiocManager::install("DESeq2")
  ```
  
  <H3 id="Bedtools">Bedtools</H3>
  TFEA uses Bedtools to do several genomic computations. Instructions for installing bedtools can be found here:
  
  <a href="http://bedtools.readthedocs.io/en/latest/content/installation.html">Bedtools Installation</a>
  
  If you are on FIJI compute cluster, bedtools is available as a module:
  
  ```
  module load bedtools/2.25.0
  ```
  
  <H3 id="MEMESuite">MEME Suite</H3>
  TFEA uses the MEME suite to scan sequences from inputted bed files for motif hits using the background atcg distribution form inputted bed file regions. TFEA also uses the MEME suite to generate motif logos for html display. Instructions for downloading and installing the MEME suite can be found here:
  
  <a href="http://meme-suite.org/doc/install.html?man_type=web">MEME Download and Installation</a>
  
  If you are on FIJI compute cluster, the meme suite is available as a module:
  
  ```
  module load meme/5.0.3
  ```
  
  <H4 id="ImageMagick">Image Magick</H3>
  TFEA uses the meme2images script within MEME to produce motif logo figures. This requires Image Magick, which is a common linux utility package sometimes pre-installed on machines. To check if you have Image Magick installed try:
  
  ```
  identify -version
  ```
  
  If you do not have Image Magick installed, follow these instructions:
  
  <a href="https://imagemagick.org/script/install-source.php">Image Magick Download and Installation</a>
  
  <H3 id="FIJIModules">FIJI Modules</H3>
  Below is a summary of all FIJI modules needed to run TFEA.
  
  ```
  module load python/3.6.3
  module load python/3.6.3/matplotlib/1.5.1
  module load python/3.6.3/scipy/0.17.1
  module load python/3.6.3/numpy/1.14.1
  module load python/3.6.3/htseq/0.9.1
  module load python/3.6.3/pybedtools/0.7.10

  module load bedtools/2.25.0
  module load meme/5.0.3
  ```

<br></br>
<H2 id="Usage">Usage</H2>

Once installed, TFEA can be run from anywhere, try:

```
TFEA --help
```

To make sure TFEA is installed properly, run the following tests:

<b>*Note:*</b> If you chose to skip installations because you were going to run TFEA using the --sbatch flag, make sure you load the appropriate modules on FIJI or these tests will fail. Also, beware that the --test-full test can be memory and CPU intensive and you might get yelled at if you execute it on the FIJI head node.

```
TFEA --test-install
TFEA --test-full
```

Once you've run the above tests successfully, you should be ready to run the full version of TFEA. Below is the minimum required input to run the full TFEA ppeline. Test files are provided within the 'test_files' directory in this repository.

Using flags

```
TFEA --output ./test_files/test_output \
--bed1 ./test_files/SRR1105736.tfit_bidirs.chr22.bed ./test_files/SRR1105737.tfit_bidirs.chr22.bed \
--bed2 ./test_files/SRR1105738.tfit_bidirs.chr22.bed ./test_files/SRR1105739.tfit_bidirs.chr22.bed \
--bam1 ./test_files/SRR1105736.sorted.chr22.subsample.bam ./test_files/SRR1105737.sorted.chr22.subsample.bam \
--bam2 ./test_files/SRR1105738.sorted.chr22.subsample.bam ./test_files/SRR1105739.sorted.chr22.subsample.bam \
--label1 condition1 --label2 condition2 \
--genomefasta ./test_files/chr22.fa \
--fimo_motifs ./test_files/test_database.meme
```

Using a <A href="#ConfigurationFile">config file</A> (config file may be combined with flag inputs)

```
TFEA --config ./test_files/test_config.ini
```

On FIJI using <A href="#UsingSBATCH">sbatch</A> (supported with config or flag inputs)

```
TFEA --config ./test_files/test_config.ini --sbatch your_email@address.com
```


<H3 id="ConfigurationFile">Configuration File</H3>
TFEA can be run exclusively through the command line using flags. Alternatively, TFEA can be run using a configuration file (.ini) that takes in flags as variables. This can be helpful to keep track of different TFEA runs and because you can use variables within the config file. For documentation on config files and what you can do with them see <a href="https://docs.python.org/3.6/library/configparser.html#supported-ini-file-structure">Supported INI File Structure</a> and <a href="https://docs.python.org/3.6/library/configparser.html#interpolation-of-values">Interpolation of values (ExtendedInterpolation)</a>

<b>*Notes:*</b>

1. Section headers (ex: `[OUTPUT]`) don't matter but you need to have at least ONE section header to be a viable .ini file
2. Capitalization of variables doesn't matter
3. Feel free to specify any additional variables you like, TFEA will only parse variables that match a flag input
4. If both flag inputs and configuration file inputs are provided, TFEA uses command line flag inputs preferrentially

Below is an example of a configuration file (./test_files/test_config.ini):

  ```bash
[OUTPUT]
OUTPUT='./test_files/test_output/'
LABEL1='Condition 1'
LABEL2='Condition 2'

[DATA]
TEST_FILES='./test_files/'
BED1=[${TEST_FILES}+'SRR1105736.tfit_bidirs.chr22.bed',${TEST_FILES}+'SRR1105737.tfit_bidirs.chr22.bed']
BED2=[${TEST_FILES}+'SRR1105738.tfit_bidirs.chr22.bed',${TEST_FILES}+'SRR1105739.tfit_bidirs.chr22.bed']
BAM1=[${TEST_FILES}+'SRR1105736.sorted.chr22.subsample.bam', ${TEST_FILES}+'SRR1105737.sorted.chr22.subsample.bam']
BAM2=[${TEST_FILES}+'SRR1105738.sorted.chr22.subsample.bam', ${TEST_FILES}+'SRR1105739.sorted.chr22.subsample.bam']

[MODULES]
FIMO_MOTIFS=${TEST_FILES}+'test_database.meme'
GENOMEFASTA=${TEST_FILES}+'chr22.fa.fai'

[OPTIONS]
OUTPUT_TYPE='html'
PLOTALL=True
```


<H3 id="UsingSBATCH">Using SBATCH</H3>
Specifying the `--sbatch` flag will submit TFEA to a compute cluster assuming you are logged into one. Below are the default node configuration settings, this can be changed within cluster_scripts/run_main.sbatch. See here the sbatch code used:

  ```qsub
  #!/bin/bash

  ###Name the job
  #SBATCH --job-name=TFEA

  ###Specify the queue
  #SBATCH -p short

  ###Specify WallTime
  #SBATCH --time=24:00:00

  ### Specify the number of nodes/cores
  #SBATCH --ntasks=10

  ### Allocate the amount of memory needed
  #SBATCH --mem=20gb

  ### Set error and output locations. These will be automatically updated to the output directory.
  #SBATCH --error /scratch/Users/user/e_and_o/%x.err
  #SBATCH --output /scratch/Users/user/e_and_o/%x.out

  ### Set your email address. This is changed automatically
  #SBATCH --mail-type=ALL
  #SBATCH --mail-user=jonathan.rubin@colorado.edu

  ### Load required modules
  module purge
  module load python/3.6.3
  module load python/3.6.3/matplotlib/1.5.1
  module load python/3.6.3/scipy/0.17.1
  module load python/3.6.3/numpy/1.14.1
  module load python/3.6.3/htseq/0.9.1
  module load python/3.6.3/pybedtools/0.7.10

  module load bedtools/2.25.0
  module load meme/5.0.3

  ### now call your program

  python3 ${cmd}
  ```
<b>*Note:*</b> For TFEA to properly run a job, the python call within the sbatch script: `python3 ${cmd}` <b>MUST NOT BE CHANGED</b>


<H3 id="PreProcessedInputs">Using Pre-processed Inputs</H3>
TFEA has several pipeline elements to it that a user may bypass by providing downstream pre-processed files. These files can be generated by TFEA if running the full pipeline and may also be used to speed up reruns of TFEA. Below are the three types of pre-processed inputs, short descriptions, an example of the file, and a usage example with TFEA (in some cases there are other inputs needed to go along with the pre-processed file). If multiple pre-processed inputs specified, TFEA will use the most downstream one.

<H4>combined_file</H4>

A sorted (by chrom, start, stop) bed file containing regions of interest

Example (./test_files/test_combined_file.bed)
```
#chrom   start stop
chr22 10683195	10683999
chr22	16609343	16609405
chr22	16901069	16902599
chr22	17036962	17037636
chr22	17158022	17160214
...
```

Usage with TFEA
```
TFEA --output ./test_files/test_output \
--combined_file ./test_files/test_combined_file.bed \
--bam1 ./test_files/SRR1105736.sorted.chr22.subsample.bam ./test_files/SRR1105737.sorted.chr22.subsample.bam \
--bam2 ./test_files/SRR1105738.sorted.chr22.subsample.bam ./test_files/SRR1105739.sorted.chr22.subsample.bam \
--label1 condition1 --label2 condition2 \
--genomefasta ./test_files/chr22.fa \
--fimo_motifs ./test_files/test_database.meme
```

<H4>ranked_file</H4>

A ranked bed file with regions of interest. 

<b>*Note:*</b> Specifying a ranked_file turns off some plotting functionality

Example (./test_files/test_ranked_file.bed)

```
#chrom	start	stop
chr22	50794870	50797870
chr22	21554591	21557591
chr22	50304644	50307644
chr22	39096295	39099295
chr22	31176104	31179104
...
```

Usage with TFEA

```
TFEA --output ./test_files/test_output \
--ranked_file ./test_files/test_ranked_file.bed \
--label1 condition1 --label2 condition2 \
--genomefasta ./test_files/chr22.fa \
--fimo_motifs ./test_files/test_database.meme
```

<H4>fasta_file</H4>

A ranked fasta file with regions of interest (sequences must have unique names but these names aren't used for anything). 

<b>*Note:*</b> Specifying a fasta_file turns off some plotting functionality

Example (./test_files/test_fasta_file.bed)

```
>chr22:50794870-50797870
ccgccccacactgacgcagt...ccgcctcagcctcctaaa
>chr22:21554591-21557591
cttggggagagcagaagcca...gtgcagtggtgcaatctt
>chr22:50304644-50307644
CTGAGCACCCCCCACCAGCCA...GGAGACGGGGCCTTTGT
...
```

Usage with TFEA

```
TFEA --output ./test_files/test_output \
--fasta_file ./test_files/test_fasta_file.fa \
--label1 condition1 --label2 condition2 \
--genomefasta ./test_files/chr22.fa \
--fimo_motifs ./test_files/test_database.meme
```

<H3 id="SecondaryAnalysis">Secondary Analysis</H3>
TFEA can also perform MD-Score analysis and differential MD-Score analysis. This can be switched on easily if running the full pipeline:

```
TFEA --output ./test_files/test_output \
--combined_file ./test_files/test_combined_file.bed \
--bam1 ./test_files/SRR1105736.sorted.chr22.subsample.bam ./test_files/SRR1105737.sorted.chr22.subsample.bam \
--bam2 ./test_files/SRR1105738.sorted.chr22.subsample.bam ./test_files/SRR1105739.sorted.chr22.subsample.bam \
--label1 condition1 --label2 condition2 \
--genomefasta ./test_files/chr22.fa \
--fimo_motifs ./test_files/test_database.meme \
--md --mdd
```

These secondary analyses can also take pre-processed input similar to TFEA. See the 'Secondary Analysis Inputs' section in the <A href="#HelpMessage">help message</A> for more information.


<H3 id="HelpMessage">Help Message</H3>
Below are all the possible flags that can be provided to TFEA with a short description and default values.

```
usage: TFEA [-h] [--output OUTPUT] [--bed1 [BED1 [BED1 ...]]]
            [--bed2 [BED2 [BED2 ...]]] [--bam1 [BAM1 [BAM1 ...]]]
            [--bam2 [BAM2 [BAM2 ...]]] [--label1 LABEL1] [--label2 LABEL2]
            [--config CONFIG] [--sbatch SBATCH] [--test-install] [--test-full]
            [--combined_file COMBINED_FILE] [--ranked_file RANKED_FILE]
            [--fasta_file FASTA_FILE] [--md] [--mdd]
            [--md_bedfile1 MD_BEDFILE1] [--md_bedfile2 MD_BEDFILE2]
            [--mdd_bedfile1 MDD_BEDFILE1] [--mdd_bedfile2 MDD_BEDFILE2]
            [--md_fasta1 MD_FASTA1] [--md_fasta2 MD_FASTA2]
            [--mdd_fasta1 MDD_FASTA1] [--mdd_fasta2 MDD_FASTA2]
            [--mdd_pval MDD_PVAL] [--mdd_percent MDD_PERCENT]
            [--combine {intersect/merge,merge all,tfit clean,tfit remove small,False}]
            [--rank {deseq,fc,False}] [--scanner {fimo,genome hits}]
            [--enrichment {auc,auc_bgcorrect}] [--debug]
            [--genomefasta GENOMEFASTA] [--fimo_thresh FIMO_THRESH]
            [--fimo_motifs FIMO_MOTIFS] [--fimo_background FIMO_BACKGROUND]
            [--genomehits GENOMEHITS] [--singlemotif SINGLEMOTIF]
            [--permutations PERMUTATIONS] [--largewindow LARGEWINDOW]
            [--smallwindow SMALLWINDOW] [--dpi DPI] [--padjcutoff PADJCUTOFF]
            [--pvalcutoff PVALCUTOFF] [--plotall] [--output_type {txt,html}]
            [--cpus CPUS]

Transcription Factor Enrichment Analysis (TFEA)

optional arguments:
  -h, --help            show this help message and exit

Main Inputs:
  Inputs required for full pipeline

  --output OUTPUT, -o OUTPUT
                        Full path to output directory. If it exists, overwrite
                        its contents.
  --bed1 [BED1 [BED1 ...]]
                        Bed files associated with condition 1
  --bed2 [BED2 [BED2 ...]]
                        Bed files associated with condition 2
  --bam1 [BAM1 [BAM1 ...]]
                        Sorted bam files associated with condition 1. Must be
                        indexed.
  --bam2 [BAM2 [BAM2 ...]]
                        Sorted bam files associated with condition 2. Must be
                        indexed.
  --label1 LABEL1       An informative label for condition 1
  --label2 LABEL2       An informative label for condition 2
  --config CONFIG, -c CONFIG
                        A configuration file that a user may use instead of
                        specifying flags. Command line flags will overwrite
                        options within the config file. See examples in the
                        config_files folder.
  --sbatch SBATCH, -s SBATCH
                        Submits an sbatch (slurm) job. If specified, input an
                        e-mail address.
  --test-install, -ti   Checks whether all requirements are installed and
                        command-line runnable.
  --test-full, -t       Performs unit testing on full TFEA pipeline.

Processed Inputs:
  Input options for pre-processed data

  --combined_file COMBINED_FILE
                        A single bed file combining regions of interest.
  --ranked_file RANKED_FILE
                        A bed file containing each regions rank as the 4th
                        column.
  --fasta_file FASTA_FILE
                        A fasta file containing sequences to be analyzed,
                        ranked by the user.

Secondary Analysis Inputs:
  Input options for performing MD-Score and Differential MD-Score analysis

  --md                  Switch that controls whether to perform MD analysis.
  --mdd                 Switch that controls whether to perform differential
                        MD analysis.
  --md_bedfile1 MD_BEDFILE1
                        A bed file for MD-Score analysis associated with
                        condition 1.
  --md_bedfile2 MD_BEDFILE2
                        A bed file for MD-Score analysis associated with
                        condition 2.
  --mdd_bedfile1 MDD_BEDFILE1
                        A bed file for Differential MD-Score analysis
                        associated with condition 1.
  --mdd_bedfile2 MDD_BEDFILE2
                        A bed file for Differential MD-Score analysis
                        associated with condition 2.
  --md_fasta1 MD_FASTA1
                        A fasta file for MD-Score analysis associated with
                        condition 1.
  --md_fasta2 MD_FASTA2
                        A fasta file for MD-Score analysis associated with
                        condition 2.
  --mdd_fasta1 MDD_FASTA1
                        A fasta file for Differential MD-Score analysis
                        associated with condition 1.
  --mdd_fasta2 MDD_FASTA2
                        A fasta file for Differential MD-Score analysis
                        associated with condition 2.
  --mdd_pval MDD_PVAL   P-value cutoff for retaining differential regions.
                        Default: 0.2
  --mdd_percent MDD_PERCENT
                        Percentage cutoff for retaining differential regions.
                        Default: False

Module Switches:
  Switches for different modules

  --combine {intersect/merge,merge all,tfit clean,tfit remove small,False}
                        Method for combining input bed files
  --rank {deseq,fc,False}
                        Method for ranking combined bed file
  --scanner {fimo,genome hits}
                        Method for scanning fasta files for motifs
  --enrichment {auc,auc_bgcorrect}
                        Method for calculating enrichment
  --debug               Print memory and CPU usage to stderr

Fasta Options:
  Options for performing conversion of bed to fasta

  --genomefasta GENOMEFASTA
                        Genomic fasta file

Scanner Options:
  Options for performing motif scanning

  --fimo_thresh FIMO_THRESH
                        P-value threshold for calling FIMO motif hits.
                        Default: 1e-6
  --fimo_motifs FIMO_MOTIFS
                        Full path to a .meme formatted motif databse file.
                        Some databases included in motif_databases folder.
  --fimo_background FIMO_BACKGROUND
                        Options for choosing mononucleotide background
                        distribution to use with FIMO. {'largewindow',
                        'smallwindow', int, file}
  --genomehits GENOMEHITS
                        A folder containing bed files with pre-calculated
                        motif hits to a genome. For use with 'genome hits'
                        scanner option.
  --singlemotif SINGLEMOTIF
                        Option to run analysis on a subset of motifs within
                        specified motif database or genome hits. Can be a
                        single motif or a comma-separated list of motifs.

Enrichment Options:
  Options for performing enrichment analysis

  --permutations PERMUTATIONS
                        Number of permutations to perfrom for calculating
                        p-value. Default: 1000
  --largewindow LARGEWINDOW
                        The size (bp) of a large window around input regions
                        that captures background. Default: 1500
  --smallwindow SMALLWINDOW
                        The size (bp) of a small window arount input regions
                        that captures signal. Default: 150

Output Options:
  Options for the output.

  --dpi DPI             Resolution of output figures. Default: 100
  --padjcutoff PADJCUTOFF
                        A p-adjusted cutoff value that determines some
                        plotting output.
  --pvalcutoff PVALCUTOFF
                        A p-value cutoff value that determines some plotting
                        output.
  --plotall             Plot graphs for all motifs.Warning: This will make
                        TFEA run much slower andwill result in a large output
                        folder.
  --output_type {txt,html}
                        Specify output type. Selecting html will increase
                        processing time and memory usage. Default: txt

Miscellaneous Options:
  Other options.

  --cpus CPUS           Number of processes to run in parallel. Note:
                        Increasing this value will significantly increase
                        memory footprint. Default: 1
```

<br></br>

<H2 id="ExampleOutput">Example Output</H2>
TFEA will output all files and folders into the directory specified by the `--output` flag. The output directory structure is as follows:

```
test_output
│   rerun.sh
│   results.txt
│   md_results.txt
│   mdd_results.txt
│   results.html
│   summary.html
│
└───e_and_o
│      TFEA_test_output.err
│      TFEA_test_output.out
│  
└───plots
│      logo_rcMOTIF.eps
│      logo_rcMOTIF.png
│      logoMOTIF.eps
│      logoMOTIF.png
│      MOTIF_enrichment_plot.png
│      MOTIF_simulation_plot.png
│      MOTIF.results.html
│      
└───temp_files
       combined_file.mergeall.bed
       count_file.bed
       count_file.header.bed
       DESeq.R
       DESeq.Rout
       DESeq.res.txt
       markov_background.txt
       ranked_file.bed
       ranked_file.fa
```

This part is still under construction.

<br></br>

<H2 id="ContactInformation">Contact Information</H2>
<a href="mailto:jonathan.rubin@colorado.edu">Jonathan.Rubin@colorado.edu</a>

