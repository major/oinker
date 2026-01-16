# 📝 DNS

DNS record management operations and types.

## Operations

### AsyncDNSAPI

::: oinker.dns.AsyncDNSAPI
    options:
      members:
        - list
        - get
        - get_by_name_type
        - create
        - edit
        - edit_by_name_type
        - delete
        - delete_by_name_type

### SyncDNSAPI

::: oinker.dns.SyncDNSAPI
    options:
      members:
        - list
        - get
        - get_by_name_type
        - create
        - edit
        - edit_by_name_type
        - delete
        - delete_by_name_type

## Record Types

All record types validate their content on construction.

### ARecord

::: oinker.ARecord

### AAAARecord

::: oinker.AAAARecord

### MXRecord

::: oinker.MXRecord

### TXTRecord

::: oinker.TXTRecord

### CNAMERecord

::: oinker.CNAMERecord

### ALIASRecord

::: oinker.ALIASRecord

### NSRecord

::: oinker.NSRecord

### SRVRecord

::: oinker.SRVRecord

### TLSARecord

::: oinker.TLSARecord

### CAARecord

::: oinker.CAARecord

### HTTPSRecord

::: oinker.HTTPSRecord

### SVCBRecord

::: oinker.SVCBRecord

### SSHFPRecord

::: oinker.SSHFPRecord

## Response Types

### DNSRecordResponse

::: oinker.DNSRecordResponse
