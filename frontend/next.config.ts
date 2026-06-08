import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname, ".."),
  env: {
    NEXT_PUBLIC_BUILD_ID:
      process.env.VERCEL_GIT_COMMIT_SHA ??
      process.env.VERCEL_DEPLOYMENT_ID ??
      process.env.GITHUB_SHA ??
      process.env.NEXT_PUBLIC_BUILD_ID ??
      "local-dev"
  }
};

export default nextConfig;
