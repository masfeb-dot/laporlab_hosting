import dns.resolver

def dns_query_specific_nameserver(query="techoverflow.net", nameserver="0.0.0.0", qtype="A"):
    """
    Query a specific nameserver for:
    - An IPv4 address for a given hostname (qtype="A")
    - An IPv6 address for a given hostname (qtype="AAAA")
    
    Returns the IP address as a string
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [nameserver]
    answer = resolver.resolve(query, qtype)

    if len(answer) == 0:
        return None
    else:
        return str(answer[0])

dns_query_specific_nameserver(qtype="A")