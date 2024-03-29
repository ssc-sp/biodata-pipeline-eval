# **Bioinformatics Pipeline Evaluation**

- [**Bioinformatics Pipeline Evaluation**](#bioinformatics-pipeline-evaluation)
  - [**Takeaways**](#takeaways)
  - [**Introduction**](#introduction)
  - [**Results**](#results)
  - [**QIIME2**](#qiime2)
    - [**Databricks**](#databricks)
      - [Troubleshooting](#troubleshooting)
      - [Performance Evaluation](#performance-evaluation)
      - [Additional Work](#additional-work)
      - [Custom Docker Image of QIIME2](#custom-docker-image-of-qiime2)
      - [Results and Takeaways](#results-and-takeaways)
    - [**Replicating on AAW**](#replicating-on-aaw)
      - [Remote Desktop environment](#remote-desktop-environment)
      - [Notebook environment](#notebook-environment)
      - [Pipeline environment](#pipeline-environment)
  - [**ATLAS**](#atlas)
    - [**Databricks**](#databricks-1)
      - [Troubleshooting](#troubleshooting-1)
    - [**Replicating on AAW**](#replicating-on-aaw-1)
  - [**R_ODAF Health Canada**](#r_odaf-health-canada)
    - [**Databricks**](#databricks-2)
      - [Troubleshooting](#troubleshooting-2)

## **Takeaways**

| Platform | Takeaways |
|----------|-----------|
|     **Databricks (NRCan DataHub)**     |  <ul><li><span style="color:green">Provides an interface closer to cluster resources (easy cluster management and monitoring).</span></li><li> <span style="color:green">Requires less work on user side to adapt for efficient resource use (in python, switching from Pandas to PySpark).</span></li><li> <span style="color:green">Provides quick and effective collaboration between users.</span></li> <li><span style="color:red">Provides less control over custom images, requiring the need of an admin to create custom images. This is still being explored and may simply come from our lack of understanding of the platform.</span></li></ul>       |
|     **Kubeflow (StatCan AAW)**     |      <ul><li><span style="color:green">Provides a JupyterLab interface which allows for the creation of custom conda environments and allows users to run notebooks directly within those environments. This is very valuable in a scientific environment.</span></li> <li><span style="color:red">Pipelining in this environment requires a good amount of adaptation work: containerizing your workflow as well as integrating it in the Kubeflow Pipeline environment.</span></li><li><span style="color:red">The quality of the documentation, specifically for Kubeflow Pipeline, is quite low in addition to be inconsistent.</span></li></ul>     |

## **Introduction**

As part of explorative work within Shared Services Canada's Science Program Federal Science DataHub initiative, two existing platforms (Databricks and AAW's Kubeflow) and their toolsets were evaluated. The goal of these evaluations was to gain an understanding of the work a typical user would go through to move their existing pipelines to these previously mentioned platforms. Two biogenomics use cases were presented to us, QIIME2 and ATLAS, which we attempted to replicate in Natural Resources Canada's Databricks and Statistics Canada's Advanced Analytics Workspace (AAW), which leverages Kubeflow.

## **Results**

We attempted to run bioinformatics pipelines using QIIME2 and Metagenome-ATLAS on several different platforms. The work completed is described here for each of the tools. 

We were forced to use the Shell to successfully run QIIME2 in Databricks as there is no way to change what conda environment a notebook uses.

We were not able to completely run the ATLAS pipeline in Databricks.

We were unable to run the sample pipeline provided in the tutorial in its entirety on Databricks. While ATLAS appears to be fully installed and setup properly using our script, we encounter a bug towards the end of execution that prevents us from finishing. 

While it seems possible to run an ATLAS pipeline in Databricks, we also encounter some of the same challenges as with QIIME2, as we were not able to set up and activate a conda environment within the cells.

As for the exploration work done in the StatCan AAW platform: we were able to run QIIME2 in their Kubeflow environment but were not able to make full use of the cluster as it is required to use the Kubeflow pipeline to fully make use.

Running ATLAS in the Kubeflow environment was unsuccessful as we ran into several problems. These problems had not been encountered by others online and very little documentation exists on how to fix them

## **QIIME2**

We found that replicating QIIME in StatCan’s platform was slightly difficult due to issues with conda environments. These issues seem to have been tied with package installation/JFROG XRAY and were fixed after contacting the StatCan AAW team on Slack. On the other hand, a few features found on AAW seemed quite useful in the context of deploying pipelines. One such feature is the creation of notebooks from within an existing conda environment.

We successfully ran the QIIME pipeline in Databricks by using Shell commands within cells to run it. This is because Databricks does not allow us to activate a conda environment, meaning we are unable to fully leverage notebooks on Databricks. StatCan's platform allows us to start notebooks with a different environment.

### **Databricks**

#### Troubleshooting

We met with Guillaume to discuss what his issue was. He was running into an issue with the ITS training script as well as the actual pipeline. We were able to replicate these issues on our end as well. 

Once we were able to replicate the issues, we worked on the QIIME Setup v2 script. We were able to resolve the issue with it by modifying some of the paths, and this script could then run fully, as shown below:

![Error picture](./assets/Picture1.png)

We then worked on the QIIME_ITS_run script. The first error encountered was an issue with the data provided, as empty values were not being removed from the fastq entries. There was a script failing to run to remove these empty values, but it was not being properly found.

 - Problem: `[Errno 2] No such file or directory for remove_empty_fastq_entries.py`
 - Cause: Program was looking in the root directory (with /remote_empty_fastq_entries.py) rather than locally.
 - Solution: Copy the script to the root with cp remove_empty_fastq_entries.py /remove_empty_fastq_entries.py. In the future, this should be resolved in the code.
  
There were additional issues regarding writing files needed for the pipeline to run. , so setting the output folder to mounted storage would cause an `OSError: [Errno 95] Operation not supported error`.

 - Problem: `OSError: [Errno 95] Operation not supported when attempting to write to the mounted storage. Failing to write also causes [Errno 2] No such file or directory since those files cannot be read later in the program.`
 - Cause: Databricks does not support writing to mounted storage.
 - Solution: Create a local directory (in our case, /tmp/qiime_test) that the pipeline can write to instead of mounted storage. Pass that as the output directory using -o /tmp/qiime_test in the call to Python. This resolves all errors.

With these errors solved, the pipeline runs properly and can be evaluated, as shown below:

![Error picture](./assets/Picture2.png)

#### Performance Evaluation
After successfully running the program, we wanted to evaluate the performance on the Databricks cluster. To do this, we started by following the code performance measurement guide here: Python Code Performance Measurement – Measure the right metric to optimize better!

We placed the starting blocks prior to running the script, then the ending blocks immediately after. We obtained the following results:

```
Peak Size in MB -  0.23340892791748047
Time elapsed: 356474.1015434265 milli seconds
```

These results can be compared by running the same code elsewhere.

#### Additional Work

We attempted to determine if QIIME2 could be added to the existing environment on Databricks. This would allow us to create notebooks that directly use QIIME2, rather than having to use shell commands to do so. 

We followed the instructions at https://docs.qiime2.org/2022.2/install/native/ to attempt the installation. This was unsuccessful, as **[conda env create and conda activate are not supported on Databricks](https://databricks.com/blog/2020/06/17/simplify-python-environment-management-on-databricks-runtime-for-machine-learning-using-pip-and-conda.html)**. Attempting to do so results in `ValueError: conda activate is not supported in Databricks.`

We also attempted the following methods to add QIIME2:

| Command | Result |
| ---     | ---    |
| `%conda env update --file qiime2_2022_4_py38_linux_conda.yml --prune` | `CalledProcessError: Command 'conda env update -p /local_disk0/.ephemeral_nfs/envs/pythonEnv-caed3ba9-87f4-4939-a9dd-a6b06d8675db --file qiime2_2022_4_py38_linux_conda.yml --prune' returned non-zero exit status 1.` |
| `!conda env update --file qiime2_2022_4_py38_linux_conda.yml --prune` | Runs without error, produces no output but does not allow `import qiime2` to be run.
| `!conda install -c qiime2 qiime2` | Runs without error, produces no output but does not allow `import qiime2` to be run. |

We were unable to directly add QIIME2 to the Databricks Conda environment. So far, the only way we can successfully use QIIME2 is by using the `%sh` command in a notebook cell to run the Shell commands needed to do so.


#### Custom Docker Image of QIIME2
One possible solution for running the QIIME2 pipeline from the Databricks Notebooks without having to use the '%sh' command in the cell, is to create a custom docker image of the QIIME2 enviornment (with all its dependncies), and use that image in the cluster. This would allow us to use the QIIME2 Python code diretly from the Notebooks.

An attempt to create this custom image using the Databricks minimal image as the base has not been successfull so far. It will require some research and some expertise in Docker to complete the bulding of this image. Once the image is ready, it can be tested on a Databricks cluster.

#### Results and Takeaways

While we were successful in running a QIIME2 pipeline, we were not able to leverage Databricks notebooks to do so. This is because setting up QIIME2 requires setting up and activating an Anaconda environment, which is not currently possible on Databricks.

The only way we were able to run the pipeline is by using the `%sh` command in a notebook cell in order to run the Shell commands necessary to setup and run QIIME2.

### **Replicating on AAW**

#### Remote Desktop environment
I have found the process of replicating this pipeline on StatCan’s platform to be slightly hard. The near necessity of using terminal forced me to use a remote desktop instead of a notebook. In the remote desktop, I have been encountering a lot of issues with setting up the proper QIIME2 environment:

![Error picture](./assets/Picture3.png)

In the first line, I create the environment from the already downloaded yml file but the process stops without completing and without throwing any errors either. Looking at `conda info --envs` shows that the environment was not properly created.
When meeting with Guillaume, he said that he encountered the exact same issue and that he had given up setting up the pipeline on StatCans platform.
This was afterwards fixed at the same time the JFROG XRAY issues were fixed (mentioned in the Notebook environment section).
From this point onward, the pipeline can be run in the Desktop environment and performance is identical to the Notebook environment.

#### Notebook environment

My goal in the notebook was to recreate the “Moving Pictures” tutorial from QIIME. Once I have done the preliminary work of getting the qiime2 conda environment setup, I tried running
```
qiime tools import --type EMPSingleEndSequences --input-path emp-single-end-sequences --output-path emp-single-end-sequences.qza
```

Which led to the same issue as we had when trying to run the pipeline on Databricks:

```
Traceback (most recent call last):
  File "/opt/conda/envs/qiime2/lib/python3.8/site-packages/qiime2/core/archive/archiver.py", line 180, in save
    zf.write(str(abspath), arcname=cls._as_zip_path(relpath))
  File "/opt/conda/envs/qiime2/lib/python3.8/zipfile.py", line 1776, in write
    shutil.copyfileobj(src, dest, 1024*8)
  File "/opt/conda/envs/qiime2/lib/python3.8/zipfile.py", line 1182, in close
    self._fileobj.seek(self._zipfile.start_dir)
OSError: [Errno 95] Operation not supported
```

The issue was with mounted storage: it seems you cannot write inside of mounted storage (from either StatCan’s AAW or Databricks) which causes this issue. This was fixed by writing the output to a folder outside of the mounted storage.

Next we ran into the following issues:

`'itsxpress' is not a valid file/folder`

And:
```
Plugin error from dada2:

  An error was encountered while running DADA2 in R (return code 1), please inspect stdout and stderr to learn more.

Debug info has been saved to /tmp/qiime2-q2cli-err-egwl88sf.log
There was an issue with loading the file /home/jovyan/qiime_test/stats.qza as metadata:

  Metadata file path doesn't exist, or the path points to something other than a file. Please check that the path exists, has read permissions, and points to a regular file (not a directory): /home/jovyan/qiime_test/stats.qza

  There may be more errors present in the metadata file. To get a full report, sample/feature metadata files can be validated with Keemei: https://keemei.qiime2.org

  Find details on QIIME 2 metadata requirements here: https://docs.qiime2.org/2022.2/tutorials/metadata/
```

These two issues are seemingly caused by installation errors with conda. I contacted people from StatCan’s AAW team on Slack to get some insight on how to fix these. I decided to restart the conda environment from scratch, as recently the StatCan team had been messing with jfrog security and it may have messed with my conda environment dependencies. Creating a new environment now results in python not recognizing the QIIME conda environment at all:

```
Traceback (most recent call last):
  File "qiime2_its.py", line 399, in <module>
    Qiime2(arguments)
  File "qiime2_its.py", line 59, in __init__
    self.run()
  File "qiime2_its.py", line 66, in run
    self.checks()
  File "qiime2_its.py", line 243, in checks
    raise Exception('You must activate your QIIME2 conda environment to run this script. '
Exception: You must activate your QIIME2 conda environment to run this script. "conda activate qiime2-2020.8"
```

Since then I have been looking at using QIIME without conda.
I contacted the AAW team on Slack but I was afterward able to find a solution: completely deleting my environment and restarting from scratch a third time in a row has the pipeline fully working. By this, I mean that the environment was fully created correctly and that the pipeline itself recognized all the tools. This seems to be confirming my idea that these issues were linked to package installment issues.

In order to test the performance, I ran the metrics tool when running the pipeline after escaping to bash and obtained results identical to those obtained when running from Databricks (perhaps the metrics tools we are using are not well adapted). 

After, I was able to create a new notebook from within the python conda environment. This is a feature that is not available on Databricks and may be extremely useful in our context.

![Error picture](./assets/Picture4.png)

From this notebook, I was able to run the pipeline without escaping to shell. I ran the metrics tools when doing so, which resulted in the same results than when escaping to shell.

#### Pipeline environment

The Kubeflow pipeline environment is an advanced tool and it should be considered only in cases where users want to push the optimization of their process to the max.

At this stage, I put a focus on trying to create a pipeline that estimates the value of pi using python. I wanted to use this pipeline to leverage the parallelization of containers. For this I used the following ressources:
- Approach 1 of [Calculating pi with python](https://www.geeksforgeeks.org/calculate-pi-with-python/)
- [Build a Pipeline](https://www.kubeflow.org/docs/components/pipelines/sdk/build-pipeline/)
- [Building Components](https://www.kubeflow.org/docs/components/pipelines/sdk/component-development/)
- [Building Python function-based components](https://www.kubeflow.org/docs/components/pipelines/sdk/python-function-components/)

This work and exploration is currently put on pause: a lot of difficulties were encountered when learning how to use this environment due to the lack/low quality of documentation.

## **ATLAS**

We were unable to successfully run an ATLAS pipeline in its entirety. We followed [a tutorial with samples](https://metagenome-atlas.readthedocs.io/en/latest/usage/getting_started.html#install-metagenome-atlas) but encountered a variety of errors. In Databricks, we encountered some of the same challenges as with QIIME2, as we were not able to set up and activate a conda environment within the cells.

### **Databricks**

#### Troubleshooting

To demonstrate the use of ATLAS on Databricks, I followed this tutorial: https://metagenome-atlas.readthedocs.io/en/latest/usage/getting_started.html#install-metagenome-atlas

The tutorial provides sample files to perform basic analysis. I used the following code, most of which was provided in this installation:

```
%sh
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda install mamba
mamba create -y -n atlasenv metagenome-atlas=2.9
source activate atlasenv
mkdir /tmp/atlas
cd /tmp/atlas
wget https://zenodo.org/record/3992790/files/test_reads.tar.gz
tar -xzf test_reads.tar.gz
atlas init --db-dir databases /tmp/atlas/test_reads
atlas run None --resources mem=128 --keep-going --latency-wait=30
```

I encountered several issues while doing this, such as:

 - Problem: `There is insufficient memory for the Java Runtime Environment to continue.`
 - Cause: Cluster has too little memory to run Atlas.
 - Solution: We increased the memory on the cluster, which prevented this error.

I also encountered severe latency using the suggested instructions. This was especially problematic as the script would crash anyways, taking me 3-4 hours to learn of a new failure. This was resolved by changing atlas run genome to atlas run None which only took half an hour to an hour.

This allowed faster troubleshooting, but there were still additional issues.

 - Problem: `Missing files after 5 seconds.`
 - Cause: Most likely file system latency.
 - Solution: Adding the `–latency-wait` tag to tolerate more latency. https://github.com/snakemake/snakemake/issues/1734 recommends 30 seconds.

Another problem was encountered near the end of execution:

 - Problem: `BUG: Out of jobs ready to be started, but not all files built yet`
 - Cause: Unknown. GitHub issue exists: https://github.com/snakemake/snakemake/issues/823 and https://github.com/snakemake/snakemake/issues/1687 
 - Solution: TBD

### **Replicating on AAW**

The same [instructions](https://metagenome-atlas.readthedocs.io/en/latest/usage/getting_started.html#install-metagenome-atlas) used in Databricks were used here in order to test out ATLAS within the AAW. While the errors previously mentioned were not encountered, the following error causes the pipeline to crash after about 30 minutes.
```[language]
Preparing transaction: ...working... done
Verifying transaction: ...working... done
Executing transaction: ...working... done
ERROR conda.core.link:_execute(730): An error occurred while installing package 'conda-forge::ca-certificates-2022.6.15-ha878542_0'.
Rolling back transaction: ...working... done

[Errno 38] Function not implemented: 'cacert.pem' -> '/home/jovyan/minio/standard/shared/david-rene/databases/conda_envs/3fb0b5df27a112cf74c4ebdd7a301db5/ssl/cert.pem'
()


[Atlas] CRITICAL: Command 'snakemake --snakefile /opt/conda/envs/atlasenv/lib/python3.8/site-packages/atlas/workflow/Snakefile --directory /home/jovyan/minio/standard/shared/david-rene --jobs 16 --rerun-incomplete --configfile '/home/jovyan/minio/standard/shared/david-rene/config.yaml' --nolock   --use-conda --conda-prefix /home/jovyan/minio/standard/shared/david-rene/databases/conda_envs    --resources mem=59 mem_mb=61102 java_mem=50   --scheduler greedy    --resources mem=128 --keep-going --latency-wait=30 ' returned non-zero exit status 1.
```
There exists no documentation online regarding this error. This seems like an issue with installing a certificate, which could potentially have been blocked by jfrog XRAY. At this stage, due to the lack of documentation online as well as a lack of way forward, this was put on pause.

## **R_ODAF Health Canada**

### **Databricks**

R_ODAF consists of a snakemake pipeline with a few R analysis scripts on top. In order to setup the pipeline, one can use the following two repos:

- Repo https://github.com/R-ODAF/R-ODAF_Health_Canada
- Data https://github.com/EHSRB-BSRSE-Bioinformatics/test-data/tree/main/

The Data repository contains a test script that highlights how to use the pipeline given the test data provided. This was used directly onto Databricks.

#### Troubleshooting

As a conda environment is required to run the pipeline, the Docker Conda cluster is used on Databricks to run the setup. When creating the conda environment using the ```environment.yml```, we run into errors as there are conflicts between the packages:
```
Determining conflicts:   0%|          | 0/63 [00:00<?, ?it/s]
Examining conflict for bioconductor-enrichplot bioconductor-clusterprofiler:   0%|          | 0/63 [00:00<?, ?it/s]
Examining conflict for rsem bioconductor-clusterprofiler bioconductor-deseq2 bioconductor-vsn bioconductor-org.hs.eg.db bioconductor-genomicfeatures bioconductor-quasr bioconductor-org.mm.eg.db bioconductor-enrichplot bioconductor-go.db:   2%|▏         | 1/63 [00:01<01:17,  1.25s/it]
Examining conflict for rsem bioconductor-clusterprofiler bioconductor-deseq2 bioconductor-vsn bioconductor-org.hs.eg.db bioconductor-genomicfeatures bioconductor-quasr bioconductor-org.mm.eg.db bioconductor-enrichplot bioconductor-go.db:   3%|▎         | 2/63 [00:01<00:37,  1.61it/s]
Examining conflict for bioconductor-clusterprofiler r-sfsmisc bioconductor-deseq2 r-devtools bioconductor-genomicfeatures bioconductor-quasr r-dt r-fields r-ggally r-sessioninfo r-cluster r-tidytext rsem r-dendsort anaconda-clean bioconductor-vsn r-kableextra r-vtree multiqc r-knitr r-rrcov r-data.table r-foreach bioconductor-go.db r-rvcheck r-dendextend bioconductor-rtracklayer r-plotly r-ggridges r-rcolorbrewer r-cairo bioconductor-limma bioconductor-edger r-heatmap3 bioconductor-enrichplot r-remotes r-viridis bioconductor-complexheatmap r-doparallel r-curl r-openxlsx r-tidyverse r-upsetr bioconductor-org.hs.eg.db r-biocmanager r-here snakemake bioconductor-org.mm.eg.db bioconductor-genomeinfodbdata r-ashr r-lattice r-yaml bioconductor-genomeinfodb r-magrittr r-pheatmap r-flextable r-gtools:   3%|▎         | 2/63 [00:11<00:37,  1.61it/s]
Examining conflict for bioconductor-clusterprofiler
...
```
This process is very long and is unable to resolve the conflicts and so it fails to create the environment. It was recommended online to give more leeway on the version requirements in order to fix this issue. We went through the environment file and gave as much free range as possible but this still did not fix the issue.

Afterwards, we went through the snakefile to identify which were the least requirements to run the snakefile. Once identified, we tried to create a conda environment based solely on those requirements: the environment did not resolve even after running overnight.
