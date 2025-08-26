import dns.resolver
import sys
import time
import threading
from lib import common

def authoritativeServer(domain, resolver) -> str:
    domainList = domain.split(".")
    rootDomain = ".".join(domainList[-2:])
    authoritativeDNSServer = ""
    answer = resolver.resolve(rootDomain, "NS")
    for a in answer.response.answer:
        for k in a.items.keys():
            authoritativeDNSServer = str(k)[:-1]
            return authoritativeDNSServer
    return authoritativeDNSServer

def authoritativeServerIP(domain, resolver) -> str:
    authoritativeDNSIPAwnser = resolver.resolve(domain, "A")
    for a in authoritativeDNSIPAwnser.response.answer:
        for k in a.items.keys():
            authoritativeDNSIP = str(k)
            return authoritativeDNSIP
    return ""

def domainTTL(domain, authoritativeDNS, resolver, type, verbose=False) -> int:
    try:
        answer = resolver.resolve(domain, type)
        for a in answer.response.answer:
            return int(a.ttl)
    except dns.resolver.NXDOMAIN as e:
        return -1
    except Exception as e:
        if verbose:
            print("Error getting TTL for a {} from {} at {}".format(type, domain, authoritativeDNS))
            print(e)
    return 0

def checkDomain(domain, recordType, warningsOnly, maxTTL, verbose):
    customResolver = dns.resolver.Resolver(configure=False)
    standardResolver = dns.resolver.Resolver(configure=True)
    authoritativeDNS = authoritativeServer(domain, resolver=standardResolver)
    authoritativeDNSIP = authoritativeServerIP(authoritativeDNS, resolver=standardResolver)
    customResolver.nameservers = [authoritativeDNSIP]
    ttl = domainTTL(domain=domain, authoritativeDNS=authoritativeDNS, resolver=customResolver, type=recordType)
    if ttl == -1:
        if verbose:
            print("\nThere is no DNS entry for {} at {}.".format(domain, authoritativeDNS))
    else:
        if maxTTL == 0:
            print("TTL for the {} DNS entry at {} is {}                    ".format(domain, authoritativeDNS, ttl), end="\r")
        else:
            if ttl == 0:
                print("\n⚠️ Warning: TTL for {} at {} is unknown".format(domain, authoritativeDNS))
            elif ttl > maxTTL:
                print("\n⚠️ Warning: TTL for {} at {} is {} instead of {}".format(domain, authoritativeDNS, ttl, maxTTL))
            else:
                if warningsOnly == False:
                    print("TTL for the {} DNS entry at {} is {}. Maximum TTL is {}.                     ".format(domain, authoritativeDNS, ttl, maxTTL), end="\r")

a = common.parseArgs(sys.argv)
verbose = a["v"]
listofDomains = []

if "domain" in a.keys():
    listofDomains.append(a["domain"])
elif "d" in a.keys():
    listofDomains.append(a["d"])
elif "list" in a.keys():
    listRaw = common.fileToString(a["list"])
    listofDomains.extend(listRaw.splitlines())
elif "l" in a.keys():
    listRaw = common.fileToString(a["l"])
    listofDomains.extend(listRaw.splitlines())
else:
    print("You need to specify a domain with either `-domain` or -`d`.")
    sys.exit(3)

maxTTL = 0
if "maxttl" in a.keys():
    maxTTL = int(a["maxttl"])

warningsOnly = False
if "warn" in a.keys() or "w" in a.keys():
    warningsOnly = True

recordType = "CNAME"
if "type" in a.keys():
    recordType = a["type"]

threadList = []
for domain in listofDomains:
    print("Cheking {}...                    ".format(domain, end="\r"))
    t = threading.Thread(target=checkDomain, args=(domain,recordType,warningsOnly,maxTTL,verbose,))
    t.start()
    threadList.append(t)
    time.sleep(1)
for t in threadList:
    t.join()

print("\nDone")