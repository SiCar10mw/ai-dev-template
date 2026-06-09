import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';

export default function Home() {
  return (
    <Layout title="Project Documentation" description="Curated project documentation">
      <main className="container margin-vert--xl">
        <h1>Project Documentation</h1>
        <p>This site is the public or audience-specific documentation surface for the project.</p>
        <p>
          <Link className="button button--primary" to="/docs/">
            Open Docs
          </Link>
        </p>
      </main>
    </Layout>
  );
}
