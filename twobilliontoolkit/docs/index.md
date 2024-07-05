## Pages

- [SpatialTransformer Database](pages/SpatialTransformer/Database.md)
- [SpatialTransformer Datatracker](pages/SpatialTransformer/Datatracker.md)
- [SpatialTransformer Parameters](pages/SpatialTransformer/Parameters.md)
- [SpatialTransformer Processor](pages/SpatialTransformer/Processor.md)
- [SpatialTransformer](pages/SpatialTransformer/SpatialTransformer.md)
- [GeoAttachmentSeeker](pages/GeoAttachmentSeeker.md)
- [Logger](pages/Logger.md)
- [NetworkTransfer](pages/NetworkTransfer.md)
- [RecordReviser](pages/RecordReviser.md)
- [RippleUnzipple](pages/RippleUnzipple.md)

## Project layout

    mkdocs.yml                      # The configuration file.
    docs/
        index.md                    # The documentation homepage.
        pages/
            SpatialTransformer/
                Database.md         # Documentation for the Database module
                ...
            GeoAttachmentSeeker.md  # Documentation for the attachment seeker tool
            ... 
    GeoAttachmentSeeker/
        geo_attachment_seeker.py
    Logger/
        logger.py
    NetworkTransfer/
        network_transfer.py
    RecordReviser/
        record_reviser.py
    RippleUnzipple/
        ripple_unzipple.py
    SpatialTransformer/             
        common.py 
        database.ini
        Database.py
        spatial_transformer.py
        ...

## Commands

* `mkdocs -h` - Print help message and exit.
* `mkdocs build` - Build the documentation site.
* `mkdocs serve` - Start the live-reloading docs server.

For full documentation visit [mkdocs.org](https://www.mkdocs.org).