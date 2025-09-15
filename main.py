import dns.resolver
import sys
import time
import threading
from lib import common

class DNSAnswer:
    raw = ""
    server = ""
    ttl = -1
    recordType = ""
    name = ""
    value = ""

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

def domainTTL(domain, resolver, type, verbose=False) -> DNSAnswer:
    answer = resolver.resolve(domain, type, )
    defaultR = DNSAnswer()
    defaultR.name = domain
    defaultR.raw = "unknown error"
    defaultR.recordType = type
    for a in answer.response.answer:
        try:
            resultList = str(a).split()
            result = DNSAnswer()
            result.name = str(resultList[0])[:-1]
            result.ttl = int(resultList[1])
            result.recordType = str(resultList[3])
            result.raw = str(a)
            return result
        except:
            result = DNSAnswer()
            result.name = domain
            result.raw = str(a)
            return result
    return defaultR

def checkDomain(domain, recordType, warningsOnly, maxTTL, excpectedTTL, verbose) -> list:
    retry = True
    attemptCount = 0
    results = []
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
                    r = domainTTL(domain=domain, resolver=customResolver, type=recordType)
                    r.server = hostname
                    results.append(r)
                    if r.ttl == -1:
                        print("There is no DNS entry for {} at {}.\n{}".format(domain, hostname, r.raw))
                    else:
                        if maxTTL == 0 and excpectedTTL == 0:
                            print("TTL for the {} DNS entry at {} is {}".format(domain, hostname, r.ttl))
                        else:
                            if r.ttl == 0:
                                print("⚠️ Warning: TTL for {} at {} is unknown".format(domain, hostname))
                            elif r.ttl > maxTTL and maxTTL > 0:
                                print("⚠️ Warning: TTL for {} at {} is {} instead of {}".format(domain, hostname, r.ttl, maxTTL))
                            elif r.ttl == expectedTTL:
                                if warningsOnly == False:
                                    print("TTL for {} at {} is {}".format(domain, hostname, r.ttl))
                            elif r.ttl != excpectedTTL and excpectedTTL != 0:
                                print("⚠️ Warning: TTL for {} at {} is {} instead of {}".format(domain, hostname, r.ttl, expectedTTL))
        except Exception as e:
            time.sleep(2)
            if verbose:
                print("Exception checking {}".format(domain))
            if attemptCount > 3:
                retry = False
                if verbose:
                    print("DNS checks for {} are still failing after {} attempts. Giving up.".format(domain, attemptCount))
                    print(e)
    return results

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

expectedTTL = 0
if "ttl" in a.keys():
    expectedTTL = int(a["ttl"])

warningsOnly = False
if "warn" in a.keys() or "w" in a.keys():
    warningsOnly = True

recordType = "CNAME"
if "type" in a.keys():
    recordType = a["type"]

outputFileName = ""
if "o" in a.keys():
    outputFileName = a["o"]

csvString = "Name,Value,Type,TTL,DNS Server"
for domain in listofDomains:
    if len(listofDomains) < 10:
        print("Cheking {}".format(domain))
    results = checkDomain(domain,recordType,warningsOnly,maxTTL,expectedTTL,verbose)
    for r in results:
        csvString = "{cont}\n{name},{value},{type},{ttl},{dnsServer}".format(cont=csvString, name=r.name, value=r.value, type=r.recordType, ttl=r.ttl, dnsServer=r.server)
    time.sleep(2)
if outputFileName != "":
    common.stringToFile(outputFileName, csvString)
print("\nDone")