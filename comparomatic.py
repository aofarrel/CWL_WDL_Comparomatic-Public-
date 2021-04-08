# CWL to WDL Compare-o-matic
#
# WARNING: By default this code will recursively
# delete .DS_Store files from the workdir.
# .DS_Store files store cosmetic folder stuff, like
# a folder background or order of icons, and can
# be mercilessly deleted. But if you run meticulously
# set up custom backgrounds for your folders, don't
# run this on, like, /Users/ or something.
#
# Both runs should have check_gds = True
# Both runs should be run on vcf.gz files
#
# Working directory should include at least two of the
# following folders:
# * local_WDL
# * terra_WDL
# * SB_CWL
#
# [1] vcf2gds
# For each chromosome folder, we expect...
# CWL: Output GDS, config file, job.err.log, job.out.log
# WDL: Output GDS, config file, stderr, stdout
#
# [2] uniqueIDs
# CWL: One output GDS per chr, config file, job.err.log, job.out.log
# WDL: One output GDS per chr, config file, stderr, stdout
#
# [3] check_gds
# For each chromosome folder, we expect...
# CWL: cmd.log, job.err.log, job.out.log
# WDL: Chr number, config file, stderr, stdout

import re
import os
import glob
import linecache
import hashlib


do_we_care_about_whitespace = False
do_we_care_about_paths = False


def delete_mac_nonsense():
	mac_bull = glob.glob('**/.DS_Store', recursive=True)
	for garbage_file in mac_bull:
		os.remove(garbage_file)

delete_mac_nonsense()
platforms = []

if(os.path.isdir("SB_CWL")):
	platforms.append("Seven Bridges (Stephanie's CWL)")
	md5_SBCWL_vcf2gds = {}
	for gds_file in glob.glob('SB_CWL/vcf2gds/**/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_SBCWL_vcf2gds[key] = value
	md5_SBCWL_uniqueIDs = {}
	for gds_file in glob.glob('SB_CWL/uniqueIDs/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_SBCWL_uniqueIDs[key] = value
	stdout_SBCWL_check_gds = []
	for stdout_file in glob.glob('SB_CWL/check_gds/**/job.out.log'):
		stdout_SBCWL_check_gds.append(stdout_file)

if(os.path.isdir("local_WDL")):
	platforms.append("Local Dockstore CLI (Ash's WDL)")
	md5_LCWDL_vcf2gds = {}
	for gds_file in glob.glob('local_WDL/vcf2gds/**/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_LCWDL_vcf2gds[key] = value
	md5_LCWDL_uniqueIDs = {}
	for gds_file in glob.glob('local_WDL/uniqueIDs/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_LCWDL_uniqueIDs[key] = value
	stdout_LCWDL_check_gds = []
	for stdout_file in glob.glob('local_WDL/check_gds/**/stdout'):
		stdout_LCWDL_check_gds.append(stdout_file)

if(os.path.isdir("terra_WDL")):
	platforms.append("Terra (Ash's WDL)")
	md5_TRWDL_vcf2gds = {}
	for gds_file in glob.glob('terra_WDL/vcf2gds/**/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_TRWDL_vcf2gds[key] = value
	md5_TRWDL_uniqueIDs = {}
	for gds_file in glob.glob('terra_WDL/uniqueIDs/*.gds'):
		key = os.path.basename(gds_file)
		value = hashlib.md5(open(gds_file,'rb').read()).hexdigest()
		md5_TRWDL_uniqueIDs[key] = value
	stdout_TRWDL_check_gds = []
	for stdout_file in glob.glob('terra_WDL/check_gds/**/stdout'):
		stdout_TRWDL_check_gds.append(stdout_file)

print("Checking md5s of GDS files in vcf2gds...")
for key in sorted(md5_LCWDL_vcf2gds.keys()):
	if (md5_LCWDL_vcf2gds[key] != md5_SBCWL_vcf2gds[key]
		or md5_TRWDL_vcf2gds[key] != md5_SBCWL_vcf2gds[key]
		or md5_LCWDL_vcf2gds[key] != md5_TRWDL_vcf2gds[key]):
		print("%s differ:\n\tSBCWL: %s\n\tLCWDL: %s\n\tTRWDL: %s" % (key, md5_SBCWL_vcf2gds[key], md5_LCWDL_vcf2gds[key], md5_TRWDL_vcf2gds[key]))
	else:
		print("%s match across " % key)
		for platform in platforms:
			print("\t  * %s" % platform)
	print()
print()
print("Checking md5s of GDS files in uniqueIDs...")
for key in sorted(md5_LCWDL_uniqueIDs.keys()):
	if (md5_LCWDL_uniqueIDs[key] != md5_SBCWL_uniqueIDs[key]
		or md5_TRWDL_uniqueIDs[key] != md5_SBCWL_uniqueIDs[key]
    	or md5_LCWDL_uniqueIDs[key] != md5_TRWDL_uniqueIDs[key]):
		print("%s differ:\n\tSBCWL: %s\n\tLCWDL: %s\n\tTRWDL: %s" % (key, md5_SBCWL_uniqueIDs[key], md5_LCWDL_uniqueIDs[key], md5_TRWDL_uniqueIDs[key]))
	else:
		print("%s match across:" % key)
		for platform in platforms:
			print("\t  * %s" % platform)
	print()
print()
print("On SB, do files change after calling unique variant IDs?")
for key in sorted(md5_SBCWL_vcf2gds.keys()):
	if (md5_SBCWL_vcf2gds[key] != md5_SBCWL_uniqueIDs[key]):
		print("%s differ:\n\tBefore: %s\n\tAfter:  %s" % (key, md5_SBCWL_vcf2gds[key], md5_SBCWL_uniqueIDs[key]))
	else:
		print("%s match." % key)
print()
print("On a local WDL run, do files change after calling unique variant IDs?")
for key in sorted(md5_LCWDL_uniqueIDs.keys()):
	if (md5_LCWDL_vcf2gds[key] != md5_LCWDL_uniqueIDs[key]):
		print("%s differ:\n\tBefore: %s\n\tAfter:  %s" % (key, md5_LCWDL_vcf2gds[key], md5_LCWDL_uniqueIDs[key]))
	else:
		print("%s match." % key)
print()
print("On a Terra WDL run, do files change after calling unique variant IDs?")
for key in sorted(md5_LCWDL_uniqueIDs.keys()):
	if (md5_TRWDL_vcf2gds[key] != md5_TRWDL_uniqueIDs[key]):
		print("%s differ:\n\tBefore: %s\n\tAfter:  %s" % (key, md5_TRWDL_vcf2gds[key], md5_TRWDL_uniqueIDs[key]))
	else:
		print("%s match." % key)

print()
print("Let's check stdout for check_gds across SB and a local run.")
i = 0
cwl_line = 0
wdl_line = 4 # skip first four lines of WDL-only output
for stdout_file in stdout_SBCWL_check_gds:
	while wdl_line < len(open(stdout_LCWDL_check_gds[i]).readlines()):
		cwl_line = cwl_line + 1
		wdl_line = wdl_line + 1
		with open(stdout_file, 'r') as file1:
			SB_stdout = linecache.getline(stdout_file, cwl_line)
		with open(stdout_LCWDL_check_gds[i], 'r') as file2:
			localWDL_stdout = linecache.getline(stdout_LCWDL_check_gds[i], wdl_line)
		if SB_stdout!=localWDL_stdout:
			if re.sub(" +", " ", SB_stdout)==re.sub(" +", " ", localWDL_stdout):
				if (do_we_care_about_whitespace):
					print("Difference detected in line %s" % cwl_line)
					print("   ...but it's just a whitespace difference.")
					print(".............................................")
					print(".............................................")
					print()
			else:
				if "/cromwell-executions/" in localWDL_stdout:
					if (do_we_care_about_paths):
						print("Difference detected in line %s" % cwl_line)
						print("   ...but it's just a difference in a filepath.")
						print(".............................................")
						print(".............................................")
						print()
				else:
						print("Difference detected in line %s" % cwl_line)
						print("SB CWL:")
						print(re.sub(" +", " ", SB_stdout))
						print("---------")
						print("Local WDL:")
						print(re.sub(" +", " ", localWDL_stdout))
						print(".............................................")
						print(".............................................")
						print()
	i+=1
	cwl_line = 0
	wdl_line = 4
print("...done")
print()
print("Let's check stdout for check_gds across SB and Terra.")
i = 0
cwl_line = 0
wdl_line = 4 # skip first four lines of WDL-only output
for stdout_file in stdout_SBCWL_check_gds:
	while wdl_line < len(open(stdout_TRWDL_check_gds[i]).readlines()):
		cwl_line = cwl_line + 1
		wdl_line = wdl_line + 1
		with open(stdout_file, 'r') as file1:
			SB_stdout = linecache.getline(stdout_file, cwl_line)
		with open(stdout_TRWDL_check_gds[i], 'r') as file2:
			terraWDL_stdout = linecache.getline(stdout_TRWDL_check_gds[i], wdl_line)
		if SB_stdout!=terraWDL_stdout:
			if re.sub(" +", " ", SB_stdout)==re.sub(" +", " ", terraWDL_stdout):
				if (do_we_care_about_whitespace):
					print("Difference detected in line %s" % cwl_line)
					print("   ...but it's just a whitespace difference.")
					print(".............................................")
					print(".............................................")
					print()
			else:
				if "/cromwell_root/" in terraWDL_stdout:
					if (do_we_care_about_paths):
						print("Difference detected in line %s" % cwl_line)
						print("   ...but it's just a difference in a filepath.")
						print(".............................................")
						print(".............................................")
						print()
				else:
						print("Difference detected in line %s" % cwl_line)
						print("SB CWL:")
						print(re.sub(" +", " ", SB_stdout))
						print("---------")
						print("Terra WDL:")
						print(re.sub(" +", " ", terraWDL_stdout))
						print(".............................................")
						print(".............................................")
						print()
	i+=1
	cwl_line = 0
	wdl_line = 4
print("...done")