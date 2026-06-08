import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
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
