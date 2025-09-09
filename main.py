import dns.resolver
import sys
import time
import threading
from lib import common

sem = threading.Semaphore(40)

def authoritativeServers(domain, resolver) -> list:
    authoritativeServerList = []
    domainList = domain.split(".")
    rootDomain = ".".join(domainList[-2:])
    authoritativeDNSServer = ""
    answer = resolver.resolve(rootDomain, "NS")
    for a in answer.response.answer:
        for k in a.items.keys():
            authoritativeDNSServer = str(k)[:-1]
            authoritativeServerList.append(authoritativeDNSServer)
    return authoritativeServerList

def authoritativeServerListIP(domains, resolver) -> dict:
    ips = {}
    for domain in domains:
        authoritativeDNSIPList = []
        authoritativeDNSIPAwnser = resolver.resolve(domain, "A")
        for a in authoritativeDNSIPAwnser.response.answer:
            for k in a.items.keys():
                authoritativeDNSIP = str(k)
                authoritativeDNSIPList.append(authoritativeDNSIP)
            ips[domain] = authoritativeDNSIPList
    return ips

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
    sem.acquire()
    retry = True
    attemptCount = 0
    while retry:
        attemptCount = attemptCount + 1
        try:
            customResolver = dns.resolver.Resolver(configure=False)
            standardResolver = dns.resolver.Resolver(configure=True)
            authoritativeDNSList = authoritativeServers(domain, resolver=standardResolver)
            authoritativeDNSIPs = authoritativeServerListIP(authoritativeDNSList, resolver=standardResolver)
            for hostname in authoritativeDNSIPs.keys():
                ips = authoritativeDNSIPs[hostname]
                for ip in ips:
                    customResolver.nameservers = [ip]
                    ttl = domainTTL(domain=domain, authoritativeDNS=ip, resolver=customResolver, type=recordType)
                    if ttl == -1:
                        if verbose:
                            print("There is no DNS entry for {} at {}.".format(domain, hostname))
                    else:
                        if maxTTL == 0:
                            print("TTL for the {} DNS entry at {} is {}".format(domain, hostname, ttl))
                        else:
                            if ttl == 0:
                                print("⚠️ Warning: TTL for {} at {} is unknown".format(domain, hostname))
                            elif ttl > maxTTL:
                                print("⚠️ Warning: TTL for {} at {} is {} instead of {}".format(domain, hostname, ttl, maxTTL))
                            else:
                                if warningsOnly == False:
                                    print("TTL for the {} DNS entry at {} is {}. Maximum TTL is {}.".format(domain, hostname, ttl, maxTTL))
            retry = False
        except Exception as e:
            time.sleep(2)
            if verbose:
                print("Exception checking {}".format(domain))
            if attemptCount > 3:
                retry = False
                if verbose:
                    print("DNS checks for {} are still failing after {} attempts. Giving up.".format(domain, attemptCount))
                    print(e)
    sem.release()

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
    if len(listofDomains) < 10:
        print("Cheking {}".format(domain))
    t = threading.Thread(target=checkDomain, args=(domain,recordType,warningsOnly,maxTTL,verbose,))
    t.start()
    threadList.append(t)
    time.sleep(2)
for t in threadList:
    t.join()
print("\nDone")