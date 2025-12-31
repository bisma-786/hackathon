const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/query',
    createProxyMiddleware({
      target: 'http://localhost:8000', // backend address
      changeOrigin: true,
      pathRewrite: { '^/query': '/query' },
    })
  );
};
