document.addEventListener("DOMContentLoaded", () => {
    const Workspace = {
        // Configuration elements
        configForm: document.getElementById("config-form"),
        discordTokenInput: document.getElementById("discord-token"),
        serverIdInput: document.getElementById("server-id"),
        channelIdInput: document.getElementById("channel-id"),
        geminiKeyInput: document.getElementById("gemini-key"),
        saveConfigBtn: document.getElementById("save-config"),
        checkStatusBtn: document.getElementById("check-status"),
        statusDisplay: document.getElementById("status-display"),
        
        // Messages elements
        fetchMessagesBtn: document.getElementById("fetch-messages"),
        messageStatus: document.getElementById("message-status"),
        messagesContainer: document.getElementById("messages-container"),
        messagesList: document.getElementById("messages-list"),
        noMessages: document.getElementById("no-messages"),
        
        // Analysis elements
        analyzeTopicsBtn: document.getElementById("analyze-topics"),
        topicsList: document.getElementById("topics-list"),
        noTopics: document.getElementById("no-topics"),
        topicSelector: document.getElementById("topic-selector"),
        getSummaryBtn: document.getElementById("get-summary"),
        summaryContent: document.getElementById("summary-content"),
        noSummary: document.getElementById("no-summary"),
        
        // Data storage
        config: {
            discordToken: "",
            serverId: "",
            channelId: "",
            geminiKey: ""
        },
        messages: [],
        topics: [],
        currentSummary: "",
        
        async init() {
            this.loadConfigFromStorage();
            this.bindEvents();
        },
        
        bindEvents() {
            this.saveConfigBtn.addEventListener("click", () => this.saveConfig());
            this.checkStatusBtn.addEventListener("click", () => this.checkStatus());
            this.fetchMessagesBtn.addEventListener("click", () => this.fetchMessages());
            this.analyzeTopicsBtn.addEventListener("click", () => this.analyzeTopics());
            this.getSummaryBtn.addEventListener("click", () => this.getSummary());
        },
        
        loadConfigFromStorage() {
            const savedConfig = localStorage.getItem("discordAnalyzerConfig");
            if (savedConfig) {
                try {
                    const config = JSON.parse(savedConfig);
                    this.discordTokenInput.value = config.discordToken || "";
                    this.serverIdInput.value = config.serverId || "";
                    this.channelIdInput.value = config.channelId || "";
                    this.geminiKeyInput.value = config.geminiKey || "";
                    
                    this.config = config;
                } catch (e) {
                    console.error("Failed to load config from storage:", e);
                }
            }
        },
        
        saveConfig() {
            this.config = {
                discordToken: this.discordTokenInput.value,
                serverId: this.serverIdInput.value,
                channelId: this.channelIdInput.value,
                geminiKey: this.geminiKeyInput.value
            };
            
            localStorage.setItem("discordAnalyzerConfig", JSON.stringify(this.config));
            this.showStatus("Configuration saved to browser storage", "success");
        },
        
        showStatus(message, type) {
            const element = this.statusDisplay;
            element.textContent = message;
            element.classList.remove("hidden", "bg-green-100", "text-green-800", "bg-red-100", "text-red-800", "bg-yellow-100", "text-yellow-800");
            
            if (type === "success") {
                element.classList.add("bg-green-100", "text-green-800");
            } else if (type === "error") {
                element.classList.add("bg-red-100", "text-red-800");
            } else {
                element.classList.add("bg-yellow-100", "text-yellow-800");
            }
            
            element.classList.remove("hidden");
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                element.classList.add("hidden");
            }, 5000);
        },
        
        showMessageStatus(message, type) {
            const element = this.messageStatus;
            element.textContent = message;
            element.classList.remove("hidden", "bg-green-100", "text-green-800", "bg-red-100", "text-red-800", "bg-yellow-100", "text-yellow-800");
            
            if (type === "success") {
                element.classList.add("bg-green-100", "text-green-800");
            } else if (type === "error") {
                element.classList.add("bg-red-100", "text-red-800");
            } else {
                element.classList.add("bg-yellow-100", "text-yellow-800");
            }
            
            element.classList.remove("hidden");
        },
        
        validateConfig() {
            if (!this.config.discordToken || !this.config.serverId || !this.config.channelId || !this.config.geminiKey) {
                this.showStatus("Please fill in all configuration fields", "error");
                return false;
            }
            return true;
        },
        
        async checkStatus() {
            if (!this.validateConfig()) return;
            
            this.showStatus("Checking API connectivity...", "info");
            
            try {
                const response = await fetch("/check_status", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        discord_token: this.config.discordToken,
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId,
                        gemini_key: this.config.geminiKey
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "success") {
                    this.showStatus("All configurations are valid!", "success");
                } else {
                    let errorMsg = "Configuration check failed: ";
                    if (!data.discord_ok) errorMsg += "Discord token is invalid. ";
                    if (!data.gemini_ok) errorMsg += "Gemini API key is invalid. ";
                    this.showStatus(errorMsg, "error");
                }
            } catch (error) {
                this.showStatus("Connection error: " + error.message, "error");
            }
        },
        
        async fetchMessages() {
            if (!this.validateConfig()) return;
            
            // Disable button and show loading
            this.fetchMessagesBtn.disabled = true;
            this.fetchMessagesBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Fetching...';
            this.showMessageStatus("Fetching messages from Discord...", "info");
            
            try {
                // Step 1: Start the fetch process
                const response = await fetch("/fetch_messages", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        discord_token: this.config.discordToken,
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "scraping_initiated") {
                    // Show initial success message
                    this.showMessageStatus(data.message, "info");
                    
                    // Poll for completion
                    this.pollForMessages();
                } else {
                    this.showMessageStatus("Failed to fetch messages: " + data.message, "error");
                    this.resetFetchButton();
                }
            } catch (error) {
                this.showMessageStatus("Connection error: " + error.message, "error");
                this.resetFetchButton();
            }
        },
        
        resetFetchButton() {
            // Reset button state
            this.fetchMessagesBtn.disabled = false;
            this.fetchMessagesBtn.innerHTML = '<i class="fas fa-cloud-download-alt mr-2"></i> Fetch Recent Messages';
        },
        
        async pollForMessages() {
            // Poll every 2 seconds to check if messages are ready
            const pollInterval = setInterval(async () => {
                try {
                    const result = await this.checkForMessages();
                    if (result) {
                        // Messages loaded successfully, stop polling
                        clearInterval(pollInterval);
                        this.resetFetchButton();
                    }
                } catch (error) {
                    console.error("Error polling for messages:", error);
                    // On error, stop polling and reset button
                    clearInterval(pollInterval);
                    this.resetFetchButton();
                    this.showMessageStatus("Error checking message status: " + error.message, "error");
                }
            }, 2000);
            
            // Set a timeout to stop polling after 30 seconds regardless
            setTimeout(() => {
                clearInterval(pollInterval);
                this.resetFetchButton();
                this.showMessageStatus("Message fetching may still be in progress. Try viewing messages in a moment.", "info");
            }, 30000);
        },
        
        async checkForMessages() {
            try {
                const response = await fetch("/get_displayed_messages", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "success" && data.messages && data.messages.length > 0) {
                    this.messages = data.messages;
                    this.renderMessages();
                    this.showMessageStatus(`Loaded ${data.messages.length} messages`, "success");
                    return true; // Messages loaded successfully
                } else {
                    // No messages yet or error
                    return false;
                }
            } catch (error) {
                console.error("Error checking for messages:", error);
                return false;
            }
        },
        
        // Legacy display function, now automatically handled
        async displayMessages() {
            if (!this.validateConfig()) return;
            
            this.showMessageStatus("Loading messages from database...", "info");
            
            try {
                const response = await fetch("/get_displayed_messages", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "success") {
                    this.messages = data.messages;
                    this.renderMessages();
                    this.showMessageStatus(`Loaded ${data.messages.length} messages`, "success");
                } else {
                    this.showMessageStatus("Failed to load messages: " + data.message, "error");
                }
            } catch (error) {
                this.showMessageStatus("Connection error: " + error.message, "error");
            }
        },
        
        renderMessages() {
            this.messagesList.innerHTML = "";
            
            if (this.messages.length === 0) {
                this.noMessages.classList.remove("hidden");
                return;
            }
            
            this.noMessages.classList.add("hidden");
            
            this.messages.forEach(msg => {
                const timestamp = new Date(msg.timestamp).toLocaleString();
                const msgElement = document.createElement("div");
                msgElement.className = "p-2 rounded-md hover:bg-gray-200";
                
                msgElement.innerHTML = `
                    <div class="font-medium text-indigo-700">${msg.author_name}</div>
                    <div>${msg.content}</div>
                    <div class="text-xs text-gray-500">${timestamp}</div>
                `;
                
                this.messagesList.appendChild(msgElement);
            });
        },
        
        async analyzeTopics() {
            if (!this.validateConfig()) return;
            
            this.showMessageStatus("Analyzing topics with Gemini...", "info");
            
            try {
                const response = await fetch("/get_topics", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId,
                        gemini_key: this.config.geminiKey
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "success") {
                    this.topics = data.topics;
                    this.renderTopics();
                    this.updateTopicSelector();
                    this.showMessageStatus(`Found ${data.topics.length} topics`, "success");
                } else {
                    this.showMessageStatus("Failed to analyze topics: " + data.message, "error");
                }
            } catch (error) {
                this.showMessageStatus("Connection error: " + error.message, "error");
            }
        },
        
        renderTopics() {
            this.topicsList.innerHTML = "";
            
            if (this.topics.length === 0) {
                this.noTopics.classList.remove("hidden");
                return;
            }
            
            this.noTopics.classList.add("hidden");
            
            this.topics.forEach(topic => {
                const topicElement = document.createElement("div");
                topicElement.className = "p-1 text-gray-800";
                topicElement.innerHTML = `<i class="fas fa-hashtag text-indigo-500 mr-1"></i> ${topic}`;
                
                this.topicsList.appendChild(topicElement);
            });
        },
        
        updateTopicSelector() {
            this.topicSelector.innerHTML = '<option value="">Select a topic to summarize</option>';
            
            this.topics.forEach(topic => {
                const option = document.createElement("option");
                option.value = topic;
                option.textContent = topic;
                this.topicSelector.appendChild(option);
            });
        },
        
        async getSummary() {
            const selectedTopic = this.topicSelector.value;
            
            if (!selectedTopic) {
                this.showMessageStatus("Please select a topic to summarize", "error");
                return;
            }
            
            if (!this.validateConfig()) return;
            
            this.showMessageStatus(`Generating summary for topic: ${selectedTopic}...`, "info");
            this.summaryContent.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Generating summary...</div>';
            this.noSummary.classList.add("hidden");
            
            try {
                const response = await fetch("/get_summary", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        server_id: this.config.serverId,
                        channel_id: this.config.channelId,
                        gemini_key: this.config.geminiKey,
                        topic: selectedTopic
                    })
                });
                
                const data = await response.json();
                
                if (data.status === "success") {
                    this.currentSummary = data.summary;
                    this.renderSummary();
                    this.showMessageStatus("Summary generated successfully", "success");
                } else {
                    this.showMessageStatus("Failed to generate summary: " + data.message, "error");
                    this.summaryContent.innerHTML = "";
                    this.noSummary.classList.remove("hidden");
                }
            } catch (error) {
                this.showMessageStatus("Connection error: " + error.message, "error");
                this.summaryContent.innerHTML = "";
                this.noSummary.classList.remove("hidden");
            }
        },
        
        renderSummary() {
            if (!this.currentSummary) {
                this.noSummary.classList.remove("hidden");
                return;
            }
            
            this.noSummary.classList.add("hidden");
            
            // Process the summary to enhance formatting
            const formattedSummary = this.currentSummary
                .replace(/\n/g, '<br>')
                .replace(/\[([^\]]+)·([^\]]+)\]/g, '<span class="font-semibold text-indigo-700">[$1<span class="text-gray-600">·$2</span>]</span>');
            
            this.summaryContent.innerHTML = formattedSummary;
        }
    };
    
    Workspace.init();
});
