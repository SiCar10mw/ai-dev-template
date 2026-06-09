# Public Docs Site

This directory is the default public wiki/docs-site for projects created from this template.

Contributor and methodology documents live in `docs/`. Public docs live here when the project is ready to publish them.

The recommended generator is Docusaurus:

```bash
npm ci
npm run build
```

The boundary is mandatory; the generator is swappable. If a project replaces Docusaurus with MkDocs, VitePress, Docsify,
or an enterprise wiki generator, preserve the same documentation-impact gate.
