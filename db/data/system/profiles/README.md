# Profiles

*Prez systems use defined profiles to generate views for RDF data.

* `prez.ttl`
    * defines the _Alternate Representations_ profile which is available for all resources. It's the profile that lists
      all available representations (profile/format combinations) for any resource
    * links `rdfs:Resource` - the most generic RDF class - to _Alternate Representations_ representations
* `catprez.ttl`
    * defined _DCAT_, _Members_ & _OASP_ profiles
        * basic DCAT, member lists and confomance class list profiles
    * links most DCAT classes (`dcat:Catalog`, `dcat:Resource` etc.) to these
* `timeprez.ttl`
    * 