# cdn-explorer — Design contract

The product-specific design specification remains in [app/DESIGN.md](app/DESIGN.md).
Read it before changing UI, components, styles, navigation or assets. This root file is
an entry point, not a second token registry. Existing brand choices and theme scope
remain authoritative in the linked specification; resolve documentation/code drift
explicitly instead of silently restyling the product.

## Sources

- [README.md](README.md)
- [app/index.html](app/index.html)
- [app/src/App.tsx](app/src/App.tsx)
- [app/src/components/DemoBanner.module.css](app/src/components/DemoBanner.module.css)
- [app/src/components/DemoBanner.tsx](app/src/components/DemoBanner.tsx)
- [app/src/components/FileTree.module.css](app/src/components/FileTree.module.css)
- [app/src/components/FileTree.tsx](app/src/components/FileTree.tsx)
- [app/src/components/ScanLog.module.css](app/src/components/ScanLog.module.css)
- [app/src/index.css](app/src/index.css)
- [app/src/pages/ExplorePage.module.css](app/src/pages/ExplorePage.module.css)

## Agent use

Read the linked specification on demand before UI work. Neither file is automatically
loaded by its name. Prism checks both root and nested DESIGN.md files; this does not
mean both are injected into every model request. Report outstanding design/code drift
and test evidence in the change description.
