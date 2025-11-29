#!/usr/bin/env node

/**
 * Downes .env Setup Wizard
 * 
 * This interactive wizard helps users configure their .env file
 * by stepping them through the available settings.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const ENV_FILE = path.join(__dirname, '..', '.env');
const ENV_EXAMPLE = path.join(__dirname, '..', 'env.example');

// ANSI color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m',
};

function log(message, color = '') {
    console.log(`${color}${message}${colors.reset}`);
}

function logHeader(message) {
    console.log();
    log('═'.repeat(60), colors.cyan);
    log(`  ${message}`, colors.cyan + colors.bright);
    log('═'.repeat(60), colors.cyan);
    console.log();
}

function logInfo(message) {
    log(`ℹ  ${message}`, colors.dim);
}

function logSuccess(message) {
    log(`✓  ${message}`, colors.green);
}

function logWarning(message) {
    log(`⚠  ${message}`, colors.yellow);
}

// Provider configurations
const providers = {
    openai: {
        name: 'OpenAI',
        description: 'Direct OpenAI API (GPT-4, GPT-3.5, etc.)',
        baseUrl: null,
        models: ['gpt-4.1', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        keyPrefix: 'sk-',
        keyHelp: 'Get your API key from: https://platform.openai.com/api-keys',
    },
    openrouter: {
        name: 'OpenRouter',
        description: 'Access 100+ models with one API key',
        baseUrl: 'https://openrouter.ai/api/v1',
        models: ['anthropic/claude-3.5-sonnet', 'meta-llama/llama-3.1-405b', 'google/gemini-pro-1.5', 'openai/gpt-4o'],
        keyPrefix: 'sk-or-',
        keyHelp: 'Get your API key from: https://openrouter.ai/keys',
    },
    ollama: {
        name: 'Ollama (Local)',
        description: '100% Free local models - no API key needed',
        baseUrl: 'http://localhost:11434/v1',
        models: ['llama3.2', 'mistral', 'qwen2.5', 'phi3', 'deepseek-coder'],
        keyPrefix: null,
        keyHelp: 'Install from: https://ollama.ai - Then run: ollama pull llama3.2',
    },
    llamacpp: {
        name: 'llama.cpp (Local)',
        description: '100% Free local models via llama.cpp server',
        baseUrl: 'http://localhost:8080/v1',
        models: ['your-model-name'],
        keyPrefix: null,
        keyHelp: 'Download from: https://github.com/ggerganov/llama.cpp',
    },
    sageis: {
        name: 'Sage.is',
        description: 'Privacy-focused cloud LLMs',
        baseUrl: 'https://api.sage.is/v1',
        models: ['your-model-name'],
        keyPrefix: null,
        keyHelp: 'Get your API key from: https://sage.is',
    },
    together: {
        name: 'Together.ai',
        description: 'Fast cloud inference',
        baseUrl: 'https://api.together.xyz/v1',
        models: ['meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'],
        keyPrefix: null,
        keyHelp: 'Get your API key from: https://together.ai',
    },
    lmstudio: {
        name: 'LM Studio (Local)',
        description: 'Local GUI for running models',
        baseUrl: 'http://localhost:1234/v1',
        models: ['local-model'],
        keyPrefix: null,
        keyHelp: 'Download from: https://lmstudio.ai',
    },
    custom: {
        name: 'Custom OpenAI-Compatible API',
        description: 'Any OpenAI-compatible endpoint',
        baseUrl: null,
        models: [],
        keyPrefix: null,
        keyHelp: 'Enter your custom API details',
    },
};

class SetupWizard {
    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
        });
        this.config = {};
    }

    async prompt(question, defaultValue = '') {
        return new Promise((resolve) => {
            const defaultText = defaultValue ? ` ${colors.dim}[${defaultValue}]${colors.reset}` : '';
            this.rl.question(`${colors.blue}?${colors.reset} ${question}${defaultText}: `, (answer) => {
                resolve(answer.trim() || defaultValue);
            });
        });
    }

    async promptSecret(question) {
        return new Promise((resolve) => {
            // Note: In a real implementation, we'd use a library to hide input
            // For now, we'll just use regular input with a warning
            this.rl.question(`${colors.blue}?${colors.reset} ${question}: `, (answer) => {
                resolve(answer.trim());
            });
        });
    }

    async select(question, options) {
        console.log(`\n${colors.blue}?${colors.reset} ${question}\n`);
        options.forEach((opt, i) => {
            const desc = opt.description ? ` ${colors.dim}- ${opt.description}${colors.reset}` : '';
            console.log(`  ${colors.cyan}${i + 1})${colors.reset} ${opt.name}${desc}`);
        });
        console.log();
        
        while (true) {
            const answer = await this.prompt('Enter your choice (number)', '1');
            const index = parseInt(answer, 10) - 1;
            if (index >= 0 && index < options.length) {
                return options[index];
            }
            logWarning(`Please enter a number between 1 and ${options.length}`);
        }
    }

    async confirm(question, defaultValue = true) {
        const defaultText = defaultValue ? 'Y/n' : 'y/N';
        const answer = await this.prompt(`${question} (${defaultText})`, defaultValue ? 'y' : 'n');
        return answer.toLowerCase().startsWith('y');
    }

    async ensureEnvFile() {
        if (fs.existsSync(ENV_FILE)) {
            logInfo('.env file already exists');
            const overwrite = await this.confirm('Do you want to reconfigure it?', false);
            if (!overwrite) {
                log('\nKeeping existing .env file. Exiting wizard.', colors.dim);
                this.rl.close();
                process.exit(0);
            }
        } else if (fs.existsSync(ENV_EXAMPLE)) {
            logInfo('Copying env.example to .env...');
            fs.copyFileSync(ENV_EXAMPLE, ENV_FILE);
            logSuccess('Created .env from env.example');
        } else {
            logInfo('Creating new .env file...');
        }
    }

    async selectProvider() {
        const providerList = Object.entries(providers).map(([key, value]) => ({
            key,
            name: value.name,
            description: value.description,
        }));

        const selected = await this.select('Which LLM provider would you like to use?', providerList);
        return selected.key;
    }

    async configureProvider(providerKey) {
        const provider = providers[providerKey];
        
        logHeader(`Configuring ${provider.name}`);
        logInfo(provider.keyHelp);
        console.log();

        // API Key - local providers don't need real API keys
        const isLocalProvider = ['ollama', 'llamacpp', 'lmstudio'].includes(providerKey);
        
        if (isLocalProvider) {
            this.config.OPENAI_API_KEY = 'not-needed-for-local';
            logInfo('Using placeholder API key for local provider');
        } else {
            const apiKey = await this.promptSecret('Enter your API key');
            if (apiKey) {
                this.config.OPENAI_API_KEY = apiKey;
            } else {
                logWarning('No API key provided - you will need to set OPENAI_API_KEY later');
                this.config.OPENAI_API_KEY = 'your-api-key-here';
            }
        }

        // Base URL
        if (provider.baseUrl) {
            this.config.OPENAI_BASE_URL = provider.baseUrl;
            logInfo(`Base URL set to: ${provider.baseUrl}`);
        } else if (providerKey === 'custom') {
            const baseUrl = await this.prompt('Enter your API base URL (e.g., https://api.example.com/v1)');
            if (baseUrl) {
                this.config.OPENAI_BASE_URL = baseUrl;
            }
        }

        // Model selection
        if (provider.models.length > 0) {
            console.log();
            const modelOptions = provider.models.map(m => ({ name: m }));
            modelOptions.push({ name: 'Enter custom model name' });
            
            const selectedModel = await this.select('Select a model:', modelOptions);
            
            if (selectedModel.name === 'Enter custom model name') {
                this.config.LLM_MODEL = await this.prompt('Enter the model name');
            } else {
                this.config.LLM_MODEL = selectedModel.name;
            }
        } else {
            this.config.LLM_MODEL = await this.prompt('Enter the model name');
        }
    }

    async configureAdvanced() {
        logHeader('Advanced Settings (Optional)');
        
        const configureAdvanced = await this.confirm('Would you like to configure advanced settings?', false);
        
        if (!configureAdvanced) {
            this.config.LLM_TEMPERATURE = '0';
            return;
        }

        // Temperature
        console.log();
        logInfo('Temperature controls randomness: 0 = deterministic, 1 = creative');
        const temp = await this.prompt('Enter temperature', '0');
        this.config.LLM_TEMPERATURE = temp;

        // LangSmith
        console.log();
        const useLangSmith = await this.confirm('Enable LangSmith for tracing and debugging?', false);
        if (useLangSmith) {
            this.config.LANGSMITH_TRACING = 'true';
            const langsmithKey = await this.promptSecret('Enter your LangSmith API key');
            if (langsmithKey) {
                this.config.LANGSMITH_API_KEY = langsmithKey;
            }
            this.config.LANGSMITH_ENDPOINT = 'https://api.smith.langchain.com';
            this.config.LANGSMITH_PROJECT = await this.prompt('Enter LangSmith project name', 'downes');
        } else {
            this.config.LANGSMITH_TRACING = 'false';
        }

        // SearXNG
        console.log();
        const useSearx = await this.confirm('Configure SearXNG for broader search?', false);
        if (useSearx) {
            const searxUrl = await this.prompt('Enter your SearXNG instance URL', 'https://searx.tiekoetter.com');
            this.config.SEARXNG_INSTANCE_URL = searxUrl;
        }
    }

    async writeConfig() {
        logHeader('Saving Configuration');
        
        // Read existing file or create new content
        let content = '';
        if (fs.existsSync(ENV_FILE)) {
            content = fs.readFileSync(ENV_FILE, 'utf8');
        }

        // Update or append each config value
        for (const [key, value] of Object.entries(this.config)) {
            const regex = new RegExp(`^#?\\s*${key}=.*$`, 'm');
            const newLine = `${key}=${value}`;
            
            if (regex.test(content)) {
                content = content.replace(regex, newLine);
            } else {
                content += `\n${newLine}`;
            }
        }

        fs.writeFileSync(ENV_FILE, content.trim() + '\n');
        logSuccess('Configuration saved to .env');
    }

    async showSummary() {
        logHeader('Configuration Summary');
        
        for (const [key, value] of Object.entries(this.config)) {
            const displayValue = key.includes('API_KEY') && value.length > 10 
                ? value.substring(0, 8) + '...' + value.substring(value.length - 4)
                : value;
            console.log(`  ${colors.cyan}${key}${colors.reset}: ${displayValue}`);
        }

        console.log();
        logSuccess('Setup complete!');
        console.log();
        logInfo('To run Downes, use:');
        console.log(`  ${colors.green}source .env && uv run downes-agent${colors.reset}`);
        console.log();
    }

    async run() {
        logHeader('Downes Environment Setup Wizard');
        log('This wizard will help you configure your .env file.', colors.dim);
        console.log();

        try {
            await this.ensureEnvFile();
            
            const providerKey = await this.selectProvider();
            await this.configureProvider(providerKey);
            await this.configureAdvanced();
            await this.writeConfig();
            await this.showSummary();
        } catch (error) {
            if (error.message === 'readline was closed') {
                console.log('\n\nSetup cancelled.');
            } else {
                console.error('\nError during setup:', error.message);
            }
        } finally {
            this.rl.close();
        }
    }
}

// Run the wizard
const wizard = new SetupWizard();
wizard.run();
