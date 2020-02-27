
Iulian@senes
------------
As a deliverable for Task RC1, attached are a set of five example files that can be used
to test the online version of the risk calculator (RadRAT).  The selected test cases cover
most features of the online calculator: single exposure of one or multiple organs, multiple
exposures of one or multiple organs, gender selection, exposures at different ages, chronic
and acute exposures, constant doses and doses described by probability distributions,
different number of iterations and random seeds. The Excel files can be uploaded into the 
online calculator and the PDF files include expected results.


Iulian@senes
------------
Yes. Example 5 can be used to test cpu and memory intensity.  
 
Out of the five test cases, Example 5 provides the greatest challenge to the computer system.  
Example 5 includes 30 dose entries, each delivering a radiation dose to all organs of the body.
The Excel file for Example 5 is set to run 300 iterations (i.e., sample size=300) and, on our
machine, it requires about 4.5 GB of memory.  To test the computer system, decrease or increase
the number of iterations (sample size) under Adv. Settings: 100, 200, 500, 700, 1000 etc. At about
1000 iterations the memory requirements should approach or exceed 12 GB.  
 
Since our machine has only 12 GB of memory, we have a limit set to stop the calculation if we expect
the memory requirements to exceed 12 GB. The limit is calculated as the product of the number of
dose entries and the sample size. If this value is greater than 30,000 (e.g., 30 dose entries x 1000 iterations),
a message is displayed.  This limit can be customized for your machine.  We would recommend that the
machine that hosts RadRAT have as much memory as possible. 
 
When sample size is changed, the risk results will vary by a small amount especially at the upper and lower limits.
This is normal since calculations are based on a random sampling process. However, changing the sample size will
affect the cpu usage time and memory required.
