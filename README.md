# Fetching Big Query History and User Logging through Firebase

The goal of this readme file is to walk through the steps needed to fetch big query history and match that with user information from Firebase to assist with the scoring process. 

Disclaimer: The steps that are presented here will have a few manual steps here and there due to the security hurdles presented by Google Big Query. A more optimal solution will involve Terraform but due to the shortage of man power and time, we will opt for this method for now. 


A Bit Of Context

Since we have the gustil tool already installed on Digital Ocean Server, leveraging this infrastructure is a good way to go about solving this problem. 

Kindly follow the steps below closely. 


1. Login into the digital ocean server. 
2. Go to the folder “data/opendigital” 
    cd .../../data/opendigital 
3. Launch the conda environment 
    conda activate py3_7_7
4. Launch the Google SDK tool 
    gcloud init 
5. Pick Project 9 for “ironhacks-covid19-data” project. 
6. Test that everything is okay by doing 
    bq 
7. Launch the following command to get the history for the “ironhacks_covid19_data” project
    bq ls -j -a ironhacks-covid19-data
8. You will then get something like the following
     jobId                   Job Type    State      Start Time         Duration     
     -------------------------------------- ---------- --------- ----------------- ---------------- 
      42e03886-aae2-4d6a-b9a6-1979de2b735b   query      SUCCESS   06 Aug 04:00:05   0:00:00.385000  
      5264caf8-e094-4957-ab35-62df3f9d2182   query      SUCCESS   05 Aug 13:53:12   0:00:00.343000  
      2b1d6d94-89f1-441d-9155-4a5e6ed32aaf   query      SUCCESS   05 Aug 04:44:08   0:00:00.296000  
      cad3310e-0875-4718-941e-e49131693c53   query      SUCCESS   05 Aug 04:43:03   0:00:00.020000  
      6ecbf89b-7226-486c-b3df-1bbae4ec19d0   query      SUCCESS   05 Aug 04:42:33   0:00:00.300000  
      c968737c-f3c9-4b51-bfbe-be66bb83168f   query      SUCCESS   05 Aug 04:40:37   0:00:00.394000  
      bquxjob_39a05f1c_173b7a425c9           query      SUCCESS   04 Aug 04:10:08   0:00:00.017000  
9. One thing you will notice is that the job id doesn’t tell you which user is launching it. 
10. To find that out, we will definitely need to know the user email who launches this job. 
11. Remember that we DON’T allow the users to access our big query interface, so we created a custom IAM emails for them according to the user id from the firebase. 
12. To get the IAM emails that are attached to the job id, we will need to first extract the jobID column from this table and output them into a CSV file. 
13. After we have done that, we should have a CSV file that looks like the following with only the job ID and all other stuffs removed. Let’s call this file “output.csv”
    job_id
    42e03886-aae2-4d6a-b9a6-1979de2b735b
    5264caf8-e094-4957-ab35-62df3f9d2182
    2b1d6d94-89f1-441d-9155-4a5e6ed32aaf
14. In the Google SDK environment, to check the user email associated with each job, the command is 
    bq show -j <job_id> 
15. However, remember that we might have thousands of jobs, and we don’t want to do this one by one, and hence, we want to write a script to automate this. To accomplish this, put this script in the same folder as your “output.csv” file above. This script will basically loop through all job id and output all the user’s email, which is the IAM email associated with each job id. 
    #!/bin/bash
    while IFS=, read -r job_id
    do
        bq show -j "$job_id"
    done < output.csv
16. Once we run this script, we will have an output similar to the following. Note that user email is removed intentionally from the output displayed here for security reason. 


      Job Type    State      Start Time         Duration      User Email   Bytes Processed   Bytes Billed   Billing Tier   Labels  
     ---------- --------- ----------------- ---------------- ------------ ----------------- -------------- -------------- -------- 
      query      SUCCESS   05 Aug 04:44:08   0:00:00.296000       Bla Bla Bla         2432              10485760       1    


17. We will then extract the State and User Email columns from the output above through the following script for further analysis 
    #!/bin/bash
    while IFS=, read -r job_id, state
    do
        echo "$job_id and $state"
    done < output.csv


18. Lastly, we will perform whatever analysis that we need for scoring. Note that the user email extracted from here is the IAM emails and IAM emails are created using the user id, so we can match back the user id to the firebase id. 



## Summary Overview 

The repository stores the user jobs and query history from Google Big Query. It also stores data pulled from firebase

**** First Step -> Generate Keys With the Terraform Repository ****

1) Git clone the terraform repository 
2) Do the necessary installations according to the readme of the repository 
3) Copy paste the registered user id from firebase to the terraform script
4) Generated keys will have the user id

**** Second Step -> Get User Information Via Firebase ****

1) In the firebase directory, you will see two notebooks, one is "users" and the other one is "users-extra". 
2) They both serve different purpose. One gives you more information on the users. 
3) The format at which the python notebook output is in the form of JSON strings. 
4) They are multiple ways to manipulate the JSON strings, one way is to leverage grep and then output the columns. 

**** Third Step -> Retrieving User Activity on Big Query Via Google SDK  ****

1) In the CLI, you can run bq ls -j -a to retrieve jobs for all users in a project.
2) Then you can run for each job id a bq show -j <job_id> and in order to have more details you will choose to use the json response:

bq show --format=prettyjson -j job_joQEqPwOiOoBlOhDBEgKxQAlKJQ

**** Last Step ****

1) The output folder contains all the combined output 


