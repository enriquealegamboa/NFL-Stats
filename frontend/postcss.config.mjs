// PostCSS runs during the Next.js build. This registers Tailwind's plugin so
// the `@import "tailwindcss";` in globals.css is expanded into real CSS.
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};

export default config;
