import reactRefresh from "@vitejs/plugin-react-refresh";
const { resolve } = require("path");

// https://vitejs.dev/config/
export default ({ command, mode }) => {
  var config = {
    plugins: [reactRefresh()],
    root: "src/saleor-algolia-ui",
    build: {
      outDir: "../saleor_algolia/static",
      assetsDir: "static",
      rollupOptions: {
        input: {
          config: resolve(__dirname, "src", "saleor-algolia-ui", "config.html"),
        },
        output: {
          manualChunks: {
            vendor: [
              "node_modules/react/index.js",
              "node_modules/react-dom/index.js",
            ],
          },
        },
      },
    },
  };
  console.log(command);
  console.log(mode);
  return config;
};
