#!/usr/bin/env python
import sys, subprocess, os, re, shlex
from optparse import OptionParser
from ctypes.util import find_library
import cPickle as pickle
import json

# make sure we have access to required GR python modules
try:
    from gnuradio import gr;
except:
    print "Can not import GNU Radio or VOLK Modtool, please ensure your environment is set up."
    sys.exit(-1);
    
# get compiler info stored at compile time
def def_vci():      # VOLK Compiler Information
    cflags = shellexec_getout("volk-config-info --cflags", print_live=False)
    cc_ver = shellexec_getout("volk-config-info --cc", print_live=False)
    return cflags + "\n" + cc_ver

def def_gci():      # GNU Radio Compiler Information
    cflags = shellexec_getout("gnuradio-config-info --cflags", print_live=False)
    cc_ver = shellexec_getout("gnuradio-config-info --cc")
    return cflags + "\n" + cc_ver

def def_grv():      # VOLK Compiler Information
    return shellexec_getout("gnuradio-config-info --version", print_live=False)

# stdout -> return (helper)
def shellexec_getout(cmd, throw_ex=True, print_live=True, print_err=False):
    print "shellexec_long: " + str(cmd);
    try:
        p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE);
        ln = "PH";
        out = ""
        while not (ln == ""):
            ln = p.stdout.readline().rstrip('\n');
            if print_live:
                print ln;
            out = out + ln;
        if print_err:
            err = p.stderr.read();
            print err;
        return out;
    except Exception, e:
        if(throw_ex):
            raise e;
        else:
            return -1;

# we get cpu info directly after VOLK benchmarks in the hope that the cpu clock is still maxed out
def cpuinfo():
    if(os.path.isfile("/proc/cpuinfo")):
        ci = open("/proc/cpuinfo", "r");
        return ci.read();
    else:
        try:
# hw.ncpu = 24
# vendor_id      : machdep.cpu.vendor: GenuineIntel
# cpu family     : machdep.cpu.family: 6
# model          : machdep.cpu.model: 44
# model name     : machdep.cpu.brand_string: Intel(R) Xeon(R) CPU           X5650  @ 2.67GHz
# stepping       : machdep.cpu.stepping: 2
# microcode      : machdep.cpu.microcode_version: 15
# cpu MHz        : hw.cpufrequency = 2660000000
# cache size     : hw.l3cachesize: 12582912
# phisical id    : hw.physicalcpu: 12
# fpu            : (get from features)
# flags          : machdep.cpu.features: FPU VME DE PSE TSC MSR PAE MCE CX8 APIC SEP MTRR
# PGE MCA CMOV PAT PSE36 CLFSH DS ACPI MMX FXSR SSE SSE2 SS HTT TM PBE
# SSE3 PCLMULQDQ DTES64 MON DSCPL VMX SMX EST TM2 SSSE3 CX16 TPR PDCM
# SSE4.1 SSE4.2 POPCNT AES PCID
#               machdep.cpu.extfeatures: SYSCALL XD 1GBPAGE EM64T LAHF RDTSCP TSCI
# --> bogomips
# clflush_size    : hw.cachelinesize = 64 (MAYBE?)
# cache_alignment : hw.cachelinesize = 64a
# address size    : machdep.cpu.address_bits.physical: 40, machdep.cpu.address_bits.virtual: 48
            _info = ""
            _info += "processor       : " + shellexec_getout("sysctl -n hw.ncpu", print_live=False) + "\n"
            _info += "vendor_id       : " + shellexec_getout("sysctl -n machdep.cpu.vendor", print_live=False) + "\n"
            _info += "cpu family      : " + shellexec_getout("sysctl -n machdep.cpu.family", print_live=False) + "\n"
            _info += "model           : " + shellexec_getout("sysctl -n machdep.cpu.model", print_live=False) + "\n"
            _info += "model name      : " + shellexec_getout("sysctl -n machdep.cpu.brand_string", print_live=False) + "\n"
            _info += "stepping        : " + shellexec_getout("sysctl -n machdep.cpu.stepping", print_live=False) + "\n"
            _info += "microcode       : " + shellexec_getout("sysctl -n machdep.cpu.microcode_version", print_live=False) + "\n"
            _info += "cpu MHz         : " + shellexec_getout("sysctl -n hw.cpufrequency", print_live=False) + "\n"
            _info += "cache size      : " + shellexec_getout("sysctl -n hw.l3cachesize", print_live=False) + "\n"
            _info += "phisical id     : " + shellexec_getout("sysctl -n hw.physicalcpu", print_live=False) + "\n"
            features  = shellexec_getout("sysctl -n machdep.cpu.features", print_live=False)
            features += shellexec_getout("sysctl -n machdep.cpu.extfeatures", print_live=False)
            fpu_match = re.search("FPU", features)
            if fpu_match:
                _info += "fpu             : " + "yes" + "\n"
            else:
                _info += "fpu             : " + "no" + "\n"
            _info += "flags           : " + features + "\n"
            _info += "bogomips        : " + "\n"
            _info += "clflush size    : " + shellexec_getout("sysctl -n hw.cachelinesize", print_live=False) + "\n"
            _info += "cache_alignment : " + shellexec_getout("sysctl -n hw.cachelinesize", print_live=False) + "\n"
            _info += "address sizes   : " + shellexec_getout("sysctl -n machdep.cpu.address_bits.physical", print_live=False) \
                                         + shellexec_getout("sysctl -n machdep.cpu.address_bits.virtual", print_live=False) + "\n"
            _info += "power management: " + "\n"
            return _info
            
        except:
            print "do something else for OSX/Windows here"
            sys.exit(-1);

def mversion():
    # MEMINFO?
    # hw.memsize: 34359738368
    # /proc/meminfo
    pass

def kversion():
    # kern.osrevision = 199506
    # kern.version = Darwin Kernel Version 13.0.0: Thu Sep 19 22:22:27 PDT 2013; root:xnu-2422.1.72~6/RELEASE_X86_64
    try:
        kn = open("/proc/version", "r");
        return kn.read();
    except:
        print "do something else for OSX/Windows here"
        sys.exit(-1);

def main():
    # parse args
    parser = OptionParser()
    parser.add_option("-s", "--submit",
                      action="store_true", dest="submit", default=False,
                      help="submit results to stats.gnuradio.org")
    parser.add_option("-v", "--volk-compiler-info",
                      action="store", dest="vci", default=def_vci(),
                      help="compiler info file for volk")
    parser.add_option("-g", "--gr-compiler-info",
                      action="store", dest="gci", default=def_gci(),
                      help="compiler info file for GNU Radio")
    parser.add_option("-V", "--gr-version",
                      action="store", dest="grv", default=def_grv(),
                      help="GNU Radio version")
    parser.add_option("-a", "--disable-volk",
                      action="store_false", dest="dv", default=True,
                      help="disable VOLK benchmarks")
    parser.add_option("-b", "--disable-waveforms",
                      action="store_false", dest="dw", default=True,
                      help="disable Waveform benchmarks")
    (options, args) = parser.parse_args();

    # run waveform measurements 
    if(options.dw):
        print "executing GR waveform benchmarks ..."
        results_fname = "profile_results.dat"
        wfstdout = shellexec_getout("python benchmarking.py -F gr_profiler.json -o %s"%(results_fname),print_err=True);
        with open(results_fname,"rb") as fp:
            wfperf = pickle.load(fp);
        wfperf = json.dumps(wfperf);
    else:
        print "wfperf failed!"
        wfperf = "";

    # run volk measurements
    if(options.dv):
        print "executing volk_profile ..."
        perf = shellexec_getout("volk_profile -b 1");
    else:
        perf = "";

    # compile results
    ci = cpuinfo();
    kn = kversion();
    results = {"k":kn,"ci":ci, "perf":perf, "wfperf":wfperf, "vci":options.vci, "gci":options.gci, "grv":options.grv};
    print "results: %s"%( results );

    #submit performance statistics
    if(options.submit):
        print "submitting benchmark statistics to stats.gnuradio.org: "
        import urllib;
        uo = urllib.URLopener();
        uo.open("http://stats.gnuradio.org/submit",urllib.urlencode(results));
        print "done."

if __name__ == "__main__":
    main()


