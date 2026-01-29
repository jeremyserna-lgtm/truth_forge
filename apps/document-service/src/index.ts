/**
 * Express API server for document service
 */

import express from 'express';
import cors from 'cors';
import path from 'path';
import { getConfig } from './config';
import { loadSecrets } from './config/secrets';
import adminRoutes from './api/routes/admin';
import customerRoutes from './api/routes/customer';

// Load secrets from Google Cloud Secret Manager before starting server
async function startServer() {
    await loadSecrets();

    const app = express();
    const config = getConfig();

    // Middleware
    app.use(cors());
    app.use(express.json());

    // Serve static files (for customer portal UI)
    app.use('/portal', express.static(path.join(__dirname, '../public')));

    // Health check
    app.use('/health', (req, res) => {
        res.json({
            status: 'healthy',
            environment: config.environment,
            multiTenant: config.multiTenant
        });
    });

    // Portal routes
    app.use('/admin', adminRoutes);
    app.use('/customer', customerRoutes);

    // Start server
    const PORT = config.port;
    app.listen(PORT, () => {
        console.log(`🚀 Document Service running on port ${PORT}`);
        console.log(`📦 Environment: ${config.environment}`);
        console.log(`👤 Admin Portal: http://localhost:${PORT}/portal/admin.html`);
        console.log(`💬 Customer Portal: http://localhost:${PORT}/portal/index.html`);
    });

    return app;
}

// Start the server
startServer().catch(console.error);
