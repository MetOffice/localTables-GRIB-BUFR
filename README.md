
![](https://github.com/MetOffice/localTables-GRIB-BUFR/workflows/pre-commit/badge.svg)

# Repository to manage the Met Office Local Table extensions to WMO BUFR and GRIB encoding data formats. 

Here you will find the GitHub repo for maintaining the Met Office Local Table extensions to the WMO BUFR and GRIB codes (http://codes.wmo.int/). These can be found at the following webpage: http://reference.metoffice.gov.uk/grib/_grib2 once published.



## Requesting additions to a table

If you would like to request a new addition to the Met Office local tables, please create a new issue using one of our templates. These include the 'GRIB2 Local codes request form' and the 'BUFR Local codes request form'. Please include as much detail as applicable and any additional information needed will be requested via the issue comments. We will check the request against our criteria and look to publish the terms as soon as the request has been approved. 



## Workflows

There are 2 automated work flows triggering repository actions:

* on Pull Request (and change to PR):
    * check-consistency
    * builds the turtle (ttl) files from the csv tables and evaluates changes required for published content
        * this should pass, unless there are content build errors
        * checking the action log to confirm that the proposed changes are as expected is useful and important
* on merge to `master`
    * pre-commit-hook-on-master
    * merges the branch onto master
    * reruns all of the check-consistency code
    * adds the new turtle(ttl) content to master as a github action commit
    * publishes new and changed content to the registry
        * this uses action secrets, ensure the full URI username and a token are entered in the action secrets in settings  
    * note, if the push to master fails then it's best not to just rerun the pipeline
        * this is because the pipeline pushes an action commit to master, which will then conflict with a rerun (expected)
    * if there are failures (e.g. registry authentication) it is safer to create a new branch & PR from the master branch, and create a new PR for the managed publish to the registry
        * (a content free change to this readme (e.g. a space) provides a useful null-commit if needed) 
