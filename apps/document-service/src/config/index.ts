/**
 * Configuration management for document service
 * Supports multiple deployment contexts: personal, client-portal, website
 */

import { TenantType, StorageConfig, TenantFeatures } from '../types';

export interface ServiceConfig {
    port: number;
    environment: 'development' | 'production';
    multiTenant: boolean;

    // Storage configuration
    defaultStorage: StorageConfig;

    // Default tenant features
    defaultFeatures: TenantFeatures;

    // Authentication
    auth: {
        jwtSecret: string;
        apiKeyEnabled: boolean;
        allowAnonymous: boolean;
    };

    // OCR Configuration
    ocr: {
        defaultProvider: 'tesseract' | 'google-vision';
        googleVisionCredentials?: string;
    };

    // Integration settings
    integrations: {
        truthForge?: {
            enabled: boolean;
            bigQueryProject: string;
            dataset: string;
        };
        gemini?: {
            apiKey: string;
            model: string;
        };
    };
}

/**
 * Personal deployment config (Jeremy's use)
 */
export const personalConfig: ServiceConfig = {
    port: 3001,
    environment: 'development',
    multiTenant: false,

    defaultStorage: {
        type: 'local',
        path: '/Users/jeremyserna/documents'
    },

    defaultFeatures: {
        operationalDocs: true,
        knowledgeAtoms: true,
        truthForgeSync: true,
        customModels: true,
        conversationalAssistant: true
    },

    auth: {
        jwtSecret: process.env.JWT_SECRET || 'dev-secret',
        apiKeyEnabled: true,
        allowAnonymous: false
    },

    ocr: {
        defaultProvider: 'tesseract'
    },

    integrations: {
        truthForge: {
            enabled: true,
            bigQueryProject: 'truth-forge',
            dataset: 'spine'
        },
        gemini: {
            apiKey: process.env.GEMINI_API_KEY || '',
            model: 'gemini-3-pro-preview'
        }
    }
};

/**
 * Client portal deployment config
 * Multi-tenant, simplified UX, "Not_me" conversational interface
 */
export const clientPortalConfig: ServiceConfig = {
    port: 3001,
    environment: 'production',
    multiTenant: true,

    defaultStorage: {
        type: 'gcs',
        bucket: 'client-documents-production'
    },

    defaultFeatures: {
        operationalDocs: false,        // Clients only use for fine-tuning data
        knowledgeAtoms: true,
        truthForgeSync: false,         // Don't sync client data to your pipeline
        customModels: true,
        conversationalAssistant: true  // "Not_me" helps them understand completeness
    },

    auth: {
        jwtSecret: process.env.JWT_SECRET!,
        apiKeyEnabled: true,
        allowAnonymous: false
    },

    ocr: {
        defaultProvider: 'google-vision',
        googleVisionCredentials: process.env.GOOGLE_VISION_CREDENTIALS
    },

    integrations: {
        gemini: {
            apiKey: process.env.GEMINI_API_KEY!,
            model: 'gemini-3-flash-preview' // Faster for client interactions
        }
    }
};

/**
 * Get configuration based on environment
 */
export function getConfig(): ServiceConfig {
    const deploymentType = process.env.DEPLOYMENT_TYPE || 'personal';

    switch (deploymentType) {
        case 'personal':
            return personalConfig;
        case 'client-portal':
            return clientPortalConfig;
        default:
            return personalConfig;
    }
}
