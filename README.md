# msXplorerAuto

Stage 1 is being developed and tested incrementally. The current script implements Step 1 only.

## Step 1

Run `python msxplorer_auto.py` and provide the requested user, asset, and docset details. The script derives `user_name`, `user_email`, UAID_2, and asset name, then displays the user-specific Downloads path. Cleanup of the Attribute Validation Checks folder requires an explicit `y` confirmation and preserves `DM3 Attribute Checker.xlsx`.

The default Documents path is derived from the entered user name. Set `MSXPLORERAUTO_DOCUMENTS_DIR` when the Windows profile folder differs from that name. The fixed data-folder locations can be overridden with `MSXPLORERAUTO_ATTRIBUTE_VALIDATION_DIR` and `MSXPLORERAUTO_BIM_CHECKER_DIR`.

VPN password capture and persistence are intentionally deferred until after testing, as specified in the brief. The Windows file workflow should be tested on Windows; unit tests here use temporary folders and do not modify project data.

Run the focused tests with:

```sh
python -m unittest -v
```