import next from "eslint-config-next/core-web-vitals";

const config = [
  ...next,
  { ignores: [".next/**", "out/**", "next-env.d.ts"] },
  {
    // Track React Compiler migration findings while keeping the existing
    // Next.js and Hooks lint checks blocking the release.
    rules: {
      "react-hooks/immutability": "warn",
      "react-hooks/purity": "warn",
      "react-hooks/set-state-in-effect": "warn",
    },
  },
];

export default config;
