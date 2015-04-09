"""Tophat module
This module contains functions for initializing all tophat specific variables and
a wrapper that that runs tophat using those parameters on a single sample.
"""

import rnaseq_pipeline.module_helper
MODULE_HELPER = rnaseq_pipeline.module_helper

def init(param):
    """Initialization function that checks the all relevant tophat parameters

    :Parameter param: dictionary that contains all general RNASeq pipeline parameters
    """
    MODULE_HELPER.checkParameter(param, key='tophat_exec', dType=str)
    MODULE_HELPER.checkParameter(param, key='tophat_index', dType=str)
    MODULE_HELPER.checkParameter(param, key='tophat_qual', dType=str, optional=True)
    MODULE_HELPER.checkParameter(param, key='tophat_N', dType=str)
    MODULE_HELPER.checkParameter(param, key='tophat_gap_length', dType=str)
    MODULE_HELPER.checkParameter(param, key='tophat_edit_dist', dType=str)
    MODULE_HELPER.checkParameter(param, key='mate_inner_dist', dType=str)
    MODULE_HELPER.checkParameter(param, key='mate_std_dev', dType=str)



def main():
    """Main function that is run on each samples, which in turn calls runs \
    tophat on a sample.
    """
    import subprocess
    import sys
    import os
    param = MODULE_HELPER.initialize_module()
    #run create output directory
    outdir = param['module_dir']+param['stub'][param['file_index']]+'/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    #build tophat call:
    call = param['tophat_exec']+' '

    #resume option
    if param['resume_module']:
        call = call + '-R ' + outdir

    else:
        #optional quality value
        if param['tophat_qual'] != 'none':
            call = call+param['tophat_qual']+' '

        #add paired parameters if paired
        if param['paired']:
            call = call + ' --mate-inner-dist ' + param['mate_inner_dist'] + \
                   ' --mate-std-dev ' + param['mate_std_dev'] + ' '

        call = call+'-o '+outdir+' -p '+param['num_processors']+' -N '+ \
               param['tophat_N']+' --read-gap-length '+ \
               param['tophat_gap_length']+' --read-edit-dist '+ \
               param['tophat_edit_dist']+' '+param['tophat_index'] \
               +' '+ param['working_file']


        #if paired add second working file
        if param['paired']:
            call = call+' '+param['working_file2']


    param['file_handle'].write('CALL: '+call+'\n')
    output, error = subprocess.Popen(call.split(),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE).communicate()
    param['file_handle'].write(error)
    param['file_handle'].write(output)

    #error handling - checking if tophat logfile exists and if it does,
    #check if tophat was run successful
    tophat_logfile = outdir + 'logs/tophat.log'

    if not os.path.exists(tophat_logfile):
        sys.exit(0)
    else:
        log = open(tophat_logfile)
        lines_end = [line for line in log.readlines() \
                       if ' Run complete: ' in line.rstrip()]
        log.close()
        if len(lines_end) == 0:
            sys.exit(0)

    #wrap up and return the current workingfile
    MODULE_HELPER.wrapup_module(param, [outdir+'accepted_hits.bam'])




