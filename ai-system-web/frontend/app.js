const API_BASE = (() => {
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    if (window.location.port && window.location.port !== "8000") {
      return "http://localhost:8000";
    }
  }
  return window.location.origin;
})();

const elements = {
  navButtons: document.querySelectorAll(".pill-nav button"),
  heroButtons: document.querySelectorAll(".hero-actions button"),
  recommendationForm: document.getElementById("recommendation-form"),
  recommendationResults: document.getElementById("recommendation-results"),
  clusterCards: document.getElementById("cluster-cards"),
  benchmarkCollege: document.getElementById("benchmark-college"),
  benchmarkButton: document.getElementById("benchmark-button"),
  benchmarkResults: document.getElementById("benchmark-results"),
  searchFocus: document.querySelector("details[data-field=focus]"),
  filterCollege: document.getElementById("filter-college"),
  filterDelivery: document.getElementById("filter-delivery"),
  searchButton: document.getElementById("search-button"),
  programTable: document.getElementById("program-table"),
  datasetMeta: document.getElementById("dataset-meta"),
  programCount: document.getElementById("program-count"),
  collegeCount: document.getElementById("college-count"),
  clusterCount: document.getElementById("cluster-count"),
  chatbotToggle: document.getElementById("chatbot-toggle"),
  chatbotPanel: document.getElementById("chatbot-panel"),
  chatbotClose: document.getElementById("chatbot-close"),
  chatbotReset: document.getElementById("chatbot-reset"),
  chatbotMessages: document.getElementById("chatbot-messages"),
  chatbotInput: document.getElementById("chatbot-input"),
  chatbotSend: document.getElementById("chatbot-send"),
  chatbotEmoji: document.getElementById("chatbot-emoji"),
  chatbotMic: document.getElementById("chatbot-mic"),
  emojiPanel: document.getElementById("emoji-panel"),
};

const DEFAULT_GREETING =
  "Hi! I’m Olivia. Ask me about programs, colleges, recommendations, or skills.";

const profileQuestions = [
  { key: "name", prompt: "What is your name?" },
  { key: "age", prompt: "How old are you?" },
  { key: "education", prompt: "What is your education background?" },
  { key: "skills", prompt: "List your skills (comma-separated)." },
  { key: "interest", prompt: "What are your interests (comma-separated)?" },
];

const chatState = {
  started: false,
  step: 0,
  profile: {},
};

const QUESTION_STARTERS = ["what", "which", "who", "where", "when", "why", "how", "can", "do", "does", "is", "are"];

// Error handling concept: centralize logging + user-facing fallbacks.
// This keeps error messaging consistent and avoids duplicated catch blocks.
function reportUiError(context, error, options = {}) { // Logs the error and updates optional UI targets.
  // Provides a single place to enrich logs with context.
  // Safely handles missing targets or messages.
  const { target, message, mode = "text" } = options;
  console.error(`[${context}]`, error);
  if (!target || !message) return;
  if (mode === "html") {
    target.innerHTML = message;
  } else {
    target.textContent = message;
  }
}

function isQuestion(text) { // Checks whether a user input looks like a question.
  // Uses punctuation or common starters to infer intent.
  // Helps route questions to the smart reply handler.
  const trimmed = text.trim().toLowerCase();
  return (
    trimmed.endsWith("?") || QUESTION_STARTERS.some((starter) => trimmed.startsWith(starter))
  );
}

function isProfileIntent(text) { // Detects whether a user wants personalized recommendations.
  // Scans for recommendation-related keywords.
  // Drives the chat flow into profile collection.
  const input = text.toLowerCase();
  return (
    input.includes("recommend") ||
    input.includes("suggest") ||
    input.includes("best college") ||
    input.includes("match")
  );
}

const chatCache = { colleges: [] };

function scrollToSection(id) { // Smooth-scrolls to a section and updates active nav state.
  // Scrolls to the target section for navigation.
  // Toggles active styles for the selected nav item.
  document.getElementById(id).scrollIntoView({ behavior: "smooth" });
  elements.navButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.target === id);
  });
}

elements.navButtons.forEach((button) => {
  button.addEventListener("click", () => scrollToSection(button.dataset.target));
});

elements.heroButtons.forEach((button) => {
  button.addEventListener("click", () => scrollToSection(button.dataset.target));
});

async function fetchJSON(url, options = {}) { // Fetches JSON with consistent error handling.
  // Throws on non-OK responses to surface failures.
  // Logs errors for easier debugging.
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    reportUiError("API request failed", error);
    throw error;
  }
}

function createCard(title, subtitle, meta, link) { // Builds a reusable card markup for list sections.
  // Generates a consistent card layout for lists.
  // Safely handles missing subtitle, meta, or link.
  return `
    <article class="card">
      <h3>${title}</h3>
      <p>${subtitle || ""}</p>
      ${meta ? `<p class="meta">${meta}</p>` : ""}
      ${link ? `<a href="${link}" target="_blank">More details</a>` : ""}
    </article>
  `;
}

function formatDuration(item) { // Formats program duration values into a readable label.
  // Prefers year values, then month values, then program length.
  // Falls back to a not-listed label when missing.
  if (item.duration_years) {
    return `${item.duration_years} years`;
  }
  if (item.duration_months) {
    return `${item.duration_months} months`;
  }
  if (item.program_length) {
    return `${item.program_length} months`;
  }
  return "Not listed";
}

function formatFees(item) { // Formats tuition values into a readable label.
  // Joins domestic, international, and additional fee fields.
  // Returns a not-listed label when fees are absent.
  const domestic = item.tuition_domestic ? `Domestic: ${item.tuition_domestic}` : null;
  const international = item.tuition_international
    ? `International: ${item.tuition_international}`
    : null;
  const extra = item.tuition_additional ? `Additional: ${item.tuition_additional}` : null;
  return [domestic, international, extra].filter(Boolean).join(" • ") || "Not listed";
}

function renderRecommendations(recommendations) { // Renders recommendation cards or an empty-state message.
  // Builds cards for each recommendation result.
  // Displays a helpful empty state if none exist.
  if (!recommendations.length) {
    elements.recommendationResults.innerHTML = "<p>No matches found. Try adding more skills.</p>";
    return;
  }
  elements.recommendationResults.innerHTML = recommendations
    .map(
      (item) =>
        createCard(
          item.college_name,
          `Course: ${item.program_name}`,
          `Duration: ${formatDuration(item)} • Campus: ${item.campus_name || "Not listed"} • Fees: ${formatFees(
            item
          )}`,
          item.details_url || item.source_url
        )
    )
    .join("");
}

function renderClusters(clusters) {
  const entries = Object.entries(clusters);
  elements.clusterCards.innerHTML = entries
    .map(([name, info]) =>
      createCard(
        name,
        `Programs: ${info.count}`,
        `Sample: ${info.sample_programs.filter(Boolean).slice(0, 3).join(", ")}`
      )
    )
    .join("");
  elements.clusterCount.textContent = entries.length;
}

function renderBenchmark(result) { // Renders benchmarking summary for a selected college.
  // Handles empty results with a fallback message.
  // Shows total vs IT program counts and top categories.
  if (!result || !result.college) {
    elements.benchmarkResults.innerHTML = "<p>No benchmark data found.</p>";
    return;
  }
  elements.benchmarkResults.innerHTML = `
    <h3>${result.college}</h3>
    <p>Total Programs: <strong>${result.total_programs}</strong></p>
    <p>IT Programs: <strong>${result.it_programs}</strong></p>
    <p>Top IT Categories: ${result.top_categories
      .map(([name, count]) => `${name} (${count})`)
      .join(", ")}</p>
  `;
}

function renderPrograms(items) { // Renders program rows for the data explorer table.
  // Builds rows with core program fields.
  // Shows a single empty-state row when needed.
  if (!items.length) {
    elements.programTable.innerHTML = `<tr><td colspan="5">No programs found.</td></tr>`;
    return;
  }
  elements.programTable.innerHTML = items
    .map(
      (item) => `
      <tr>
        <td>${item.college_name}</td>
        <td>${item.program_name}</td>
        <td>${item.credential_type || ""}</td>
        <td>${item.delivery_format || ""}</td>
        <td>${item.program_category || ""}</td>
      </tr>
    `
    )
    .join("");
}

async function loadInitialData() {
  try {
    const [colleges, clusters, programs] = await Promise.all([
      fetchJSON(`${API_BASE}/api/colleges`),
      fetchJSON(`${API_BASE}/api/skill-clusters`),
      fetchJSON(`${API_BASE}/api/programs?limit=15`),
    ]);

    chatCache.colleges = colleges;

    elements.filterCollege.innerHTML =
      `<option value="">All Colleges</option>` +
      colleges.map((college) => `<option value="${college}">${college}</option>`).join("");
    elements.benchmarkCollege.innerHTML = colleges
      .map((college) => `<option value="${college}">${college}</option>`)
      .join("");

    renderClusters(clusters.clusters);
    renderPrograms(programs.items);

    elements.programCount.textContent = programs.total;
    elements.collegeCount.textContent = colleges.length;
    elements.datasetMeta.textContent = `Loaded ${programs.total} IT program records across ${colleges.length} colleges.`;
  } catch (error) {
    reportUiError("Initial data load", error, {
      target: elements.datasetMeta,
      message: "Unable to load API data. Make sure the backend is running.",
    });
  }
}

function getCheckedValues(container) { // Collects checked values from a details checkbox list.
  // Reads checked inputs and returns their values.
  // Guards against missing containers.
  if (!container) return [];
  return Array.from(container.querySelectorAll("input[type=checkbox]:checked")).map(
    (input) => input.value
  );
}

function updateSummaryText(detailsEl, fallback) { // Updates the summary text of a multi-select details element.
  // Replaces summary text with selected values.
  // Falls back to a default label when empty.
  if (!detailsEl) return;
  const summary = detailsEl.querySelector("summary");
  const values = getCheckedValues(detailsEl);
  summary.textContent = values.length ? values.join(", ") : fallback;
}

document.querySelectorAll(".multi-select").forEach((detailsEl) => {
  const fallback = detailsEl.querySelector("summary")?.textContent || "Select options";
  detailsEl.addEventListener("change", () => updateSummaryText(detailsEl, fallback));
});

elements.recommendationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const formData = new FormData(event.target);
    const selectedSkills = getCheckedValues(
      event.target.querySelector("details[data-field=skills]")
    );
    const selectedGoals = getCheckedValues(
      event.target.querySelector("details[data-field=goals]")
    );
    const payload = {
      education: formData.get("education") || "",
      skills: selectedSkills,
      goals: selectedGoals,
      delivery_preference: formData.get("delivery") || null,
      region_preference: formData.get("region") || null,
      max_duration_years: formData.get("duration")
        ? Number(formData.get("duration"))
        : null,
    };

    const result = await fetchJSON(`${API_BASE}/api/recommendations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    renderRecommendations(result.recommendations || []);
  } catch (error) {
    reportUiError("Recommendations", error, {
      target: elements.recommendationResults,
      message: "<p>Unable to load recommendations. Please try again.</p>",
      mode: "html",
    });
  }
});

elements.searchButton.addEventListener("click", async () => {
  try {
    const selectedFocus = getCheckedValues(elements.searchFocus)
      .filter(Boolean)
      .join(" ");
    const params = new URLSearchParams({
      query: selectedFocus || "",
      college: elements.filterCollege.value || "",
      delivery: elements.filterDelivery.value || "",
      limit: 25,
    });

    const result = await fetchJSON(`${API_BASE}/api/programs?${params.toString()}`);
    renderPrograms(result.items || []);
  } catch (error) {
    reportUiError("Program search", error, {
      target: elements.programTable,
      message: "<tr><td colspan=\"5\">Unable to load programs. Please try again.</td></tr>",
      mode: "html",
    });
  }
});

elements.benchmarkButton.addEventListener("click", async () => {
  const college = elements.benchmarkCollege.value;
  if (!college) return;
  try {
    const result = await fetchJSON(
      `${API_BASE}/api/benchmark?college=${encodeURIComponent(college)}`
    );
    renderBenchmark(result);
  } catch (error) {
    reportUiError("Benchmark load", error, {
      target: elements.benchmarkResults,
      message: "<p>Unable to load benchmark data.</p>",
      mode: "html",
    });
  }
});

loadInitialData();

function appendChatMessage(text, role = "bot") { // Appends a chat bubble to the chatbot transcript.
  // Adds a message element to the chat container.
  // Scrolls to keep the latest message in view.
  if (!elements.chatbotMessages) return;
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = text;
  elements.chatbotMessages.appendChild(message);
  elements.chatbotMessages.scrollTop = elements.chatbotMessages.scrollHeight;
}

function resetChat() { // Resets chatbot state and shows the default greeting.
  // Clears the message list and resets state.
  // Restarts the greeting for a fresh session.
  if (!elements.chatbotMessages) return;
  elements.chatbotMessages.innerHTML = "";
  appendChatMessage(DEFAULT_GREETING, "bot");
  chatState.started = false;
  chatState.step = 0;
  chatState.profile = {};
}

function getOliviaReply(question) { // Returns a simple rule-based response for common queries.
  // Uses keyword checks for fast canned responses.
  // Provides guidance to feature sections.
  const input = question.toLowerCase();

  if (input.includes("recommend")) {
    return "Use the Student Recommendations section. Choose education, skills, goals, and I will rank matching IT programs.";
  }
  if (input.includes("skill") || input.includes("cluster")) {
    return "Open Academic Advisor View to see skill clusters like Cybersecurity, Data & AI, and Software Development.";
  }
  if (input.includes("benchmark")) {
    return "In College Benchmarking, pick a college to compare total programs vs IT programs and top categories.";
  }
  if (input.includes("policy") || input.includes("region")) {
    return "Use the Data Explorer to filter programs by college and delivery format.";
  }
  if (input.includes("dashboard") || input.includes("chart")) {
    return "Use the Data Explorer to search and filter Ontario IT programs by category, college, and delivery.";
  }
  if (input.includes("data") || input.includes("dataset") || input.includes("explorer")) {
    return "Use Data Explorer to filter programs by keyword, college, and delivery format.";
  }
  if (input.includes("ai")) {
    return "This project uses AI/NLP to classify programs and recommend the best fits for student profiles.";
  }
  if (input.includes("hello") || input.includes("hi")) {
    return "Hello! I’m Olivia. Ask me about recommendations, skill clusters, or program comparisons.";
  }

  return "I can help with recommendations, skill clusters, benchmarking, policy analysis, and data explorer. Try asking about one of these.";
}

async function getOliviaSmartReply(question) { // Returns a smarter reply based on live search results.
  // Pulls search results to craft a richer reply.
  // Falls back to rule-based replies on errors.
  try {
    const result = await fetchJSON(
      `${API_BASE}/api/search?query=${encodeURIComponent(question)}&limit=6`
    );

    const parts = [];

    if (result.colleges && result.colleges.length) {
      const college = result.colleges[0];
      const topCategories = (college.top_categories || [])
        .map(([name, count]) => `${name} (${count})`)
        .join(", ");
      parts.push(
        `${college.college}: ${college.it_programs} IT programs out of ${college.total_programs}.` +
          (topCategories ? ` Top categories: ${topCategories}.` : "")
      );
    }

    if (result.programs && result.programs.length) {
      const names = result.programs
        .slice(0, 6)
        .map((item) => `${item.program_name} (${item.college_name})`)
        .filter(Boolean);
      if (names.length) {
        parts.push(`Suggested programs: ${names.join("; ")}.`);
      }
    }

    if (parts.length) {
      return parts.join(" ");
    }

    return getOliviaReply(question);
  } catch (error) {
    reportUiError("Smart reply", error);
    return "I'm having trouble accessing live data. Try again in a moment.";
  }
}

async function handleChatSend() { // Handles chatbot form input and conversation flow.
  // Manages profile collection and Q&A flow.
  // Sends recommendations when profile is complete.
  const text = elements.chatbotInput.value.trim();
  if (!text) return;
  appendChatMessage(text, "user");
  elements.chatbotInput.value = "";
  try {
    if (!chatState.started) {
      if (isProfileIntent(text)) {
        chatState.started = true;
        chatState.step = 0;
        appendChatMessage(profileQuestions[0].prompt, "bot");
        return;
      }

      if (isQuestion(text)) {
        const reply = await getOliviaSmartReply(text);
        appendChatMessage(reply, "bot");
        return;
      }

      appendChatMessage(
        "Ask me a question or say 'recommend' to start a personalized college match.",
        "bot"
      );
      return;
    }

    if (chatState.step < profileQuestions.length) {
      const { key } = profileQuestions[chatState.step];
      chatState.profile[key] = text;
      chatState.step += 1;

      if (chatState.step < profileQuestions.length) {
        appendChatMessage(profileQuestions[chatState.step].prompt, "bot");
        return;
      }

      const skills = (chatState.profile.skills || "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      const goals = (chatState.profile.interest || "")
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);

      const result = await fetchJSON(`${API_BASE}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          education: chatState.profile.education || "",
          skills,
          goals,
          limit: 8,
        }),
      });

      const recommendations = result.recommendations || [];
      const seen = new Set();
      const ordered = [];
      recommendations.forEach((item) => {
        const name = item.college_name || "Unknown College";
        if (!seen.has(name)) {
          seen.add(name);
          ordered.push({
            college: name,
            program: item.program_name || "Program",
          });
        }
      });

      if (!ordered.length) {
        appendChatMessage(
          "Thanks! I couldn't find matches yet. Try different skills or interests.",
          "bot"
        );
        return;
      }

      const list = ordered
        .slice(0, 6)
        .map((item, index) => `${index + 1}) ${item.college} — ${item.program}`)
        .join("\n");

      appendChatMessage(
        `Thanks ${chatState.profile.name || "there"}! Here are the best colleges in order:\n${list}`,
        "bot"
      );
      return;
    }

    const reply = await getOliviaSmartReply(text);
    appendChatMessage(reply, "bot");
  } catch (error) {
    reportUiError("Chat send", error);
    appendChatMessage(
      "I had trouble reaching the data service. Please try again in a moment.",
      "bot"
    );
  }
}

const on = (element, event, handler) => { // Safely wires event listeners only when elements exist.
  // Avoids attaching listeners when elements are missing.
  // Keeps event wiring concise and consistent.
  if (element) {
    element.addEventListener(event, handler);
  }
};

on(elements.chatbotToggle, "click", () => {
  if (!elements.chatbotPanel || !elements.chatbotToggle) return;
  const isOpen = elements.chatbotPanel.classList.toggle("open");
  elements.chatbotPanel.setAttribute("aria-hidden", String(!isOpen));
  elements.chatbotToggle.setAttribute("aria-expanded", String(isOpen));
});

on(elements.chatbotClose, "click", () => {
  if (!elements.chatbotPanel || !elements.chatbotToggle) return;
  elements.chatbotPanel.classList.remove("open");
  elements.chatbotPanel.setAttribute("aria-hidden", "true");
  elements.chatbotToggle.setAttribute("aria-expanded", "false");
});

on(elements.chatbotReset, "click", resetChat);
on(elements.chatbotSend, "click", handleChatSend);
on(elements.chatbotInput, "keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    handleChatSend();
  }
});

on(elements.chatbotEmoji, "click", () => {
  if (!elements.emojiPanel) return;
  const isOpen = elements.emojiPanel.classList.toggle("open");
  elements.emojiPanel.setAttribute("aria-hidden", String(!isOpen));
});

if (elements.emojiPanel) {
  elements.emojiPanel.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      if (!elements.chatbotInput) return;
      elements.chatbotInput.value += button.textContent;
      elements.chatbotInput.focus();
    });
  });
}

let recognition = null;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
}

on(elements.chatbotMic, "click", () => {
  try {
    if (!recognition) {
      appendChatMessage("Voice input is not supported in this browser.", "bot");
      return;
    }
    recognition.start();
  } catch (error) {
    reportUiError("Voice input", error);
    appendChatMessage("Voice input failed. Please try again.", "bot");
  }
});

if (recognition) {
  recognition.addEventListener("result", (event) => {
    const transcript = event.results[0][0].transcript || "";
    if (elements.chatbotInput) {
      elements.chatbotInput.value = transcript;
      elements.chatbotInput.focus();
    }
  });

  recognition.addEventListener("error", () => {
    appendChatMessage("Voice input failed. Please try again.", "bot");
  });
}

resetChat();

// ---------------------------------------------------------------------------
// ML Insights – Phase 2
// ---------------------------------------------------------------------------

function populateEvalMetrics(evalData) {
  if (evalData.status === "fitted") {
    document.getElementById("ml-silhouette").textContent =
      evalData.silhouette_score !== null ? evalData.silhouette_score : "N/A";
    document.getElementById("ml-corpus").textContent = evalData.programs_in_corpus.toLocaleString();
    document.getElementById("ml-clusters-n").textContent = evalData.n_clusters;
    document.getElementById("ml-vocab").textContent = evalData.vocabulary_size.toLocaleString();

    // Extra metrics row
    const extraEl = document.getElementById("ml-extra-metrics");
    if (extraEl) {
      document.getElementById("ml-inertia").textContent =
        evalData.inertia !== undefined ? evalData.inertia.toLocaleString() : "—";
      const sizes = evalData.cluster_sizes
        ? Object.entries(evalData.cluster_sizes)
            .sort((a, b) => b[1] - a[1])
            .map(([n, c]) => `${n}: ${c}`)
            .join(" · ")
        : "—";
      document.getElementById("ml-cluster-sizes").textContent = sizes;
      extraEl.style.display = "block";
    }

    // Top TF-IDF terms
    const termCloud = document.getElementById("ml-top-terms");
    if (termCloud && evalData.top_global_terms) {
      termCloud.innerHTML = evalData.top_global_terms
        .map(t => `<span class="tag">${t}</span>`)
        .join(" ");
    }

    // MLflow run ID badge
    const evalCard = document.getElementById("ml-eval-card");
    if (evalCard && evalData.mlflow_run_id) {
      let badge = evalCard.querySelector(".mlflow-run-id");
      if (!badge) {
        badge = document.createElement("p");
        badge.className = "mlflow-run-id";
        badge.style.cssText = "margin-top:.75rem;font-size:.8rem;color:var(--muted,#6b7280);";
        evalCard.appendChild(badge);
      }
      badge.innerHTML = `MLflow Run: <code>${evalData.mlflow_run_id}</code>`;
    }

    // Status label
    const statusEl = document.getElementById("ml-eval-status");
    if (statusEl) statusEl.textContent = "";
  } else {
    document.getElementById("ml-silhouette").textContent = "Not fitted";
    const statusEl = document.getElementById("ml-eval-status");
    if (statusEl) statusEl.textContent = evalData.reason || "Pipeline not fitted yet.";
  }
}

async function runEvaluation() {
  const btn = document.getElementById("run-eval-btn");
  const statusEl = document.getElementById("ml-eval-status");
  if (btn) { btn.disabled = true; btn.textContent = "Running…"; }
  if (statusEl) statusEl.textContent = "Fetching evaluation metrics…";

  try {
    const evalData = await fetchJSON(`${API_BASE}/api/ml-evaluation`);
    populateEvalMetrics(evalData);
    if (statusEl) statusEl.textContent = `Last run: ${new Date().toLocaleTimeString()}`;
  } catch (error) {
    reportUiError("Run Evaluation", error, {
      target: statusEl,
      message: "Failed to fetch metrics. Is the backend running?",
    });
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = "&#9654; Run Evaluation"; }
  }
}

async function loadMlInsights() {
  try {
    const [evalData, clusterData] = await Promise.all([
      fetchJSON(`${API_BASE}/api/ml-evaluation`),
      fetchJSON(`${API_BASE}/api/ml-clusters`),
    ]);

    populateEvalMetrics(evalData);

    // ML Cluster cards
    const mlClusterCards = document.getElementById("ml-cluster-cards");
    if (mlClusterCards && clusterData.clusters) {
      const entries = Object.entries(clusterData.clusters);
      mlClusterCards.innerHTML = entries
        .map(([name, info]) => `
          <article class="card">
            <h3>${name}</h3>
            <p class="meta">${info.count} programs</p>
            <p><strong>Top Terms:</strong> ${(info.top_terms || []).join(", ")}</p>
            ${info.sample_programs && info.sample_programs.length
              ? `<ul>${info.sample_programs.map(p =>
                  `<li>${p.program_name} — <em>${p.college_name}</em></li>`
                ).join("")}</ul>`
              : ""}
          </article>
        `)
        .join("");
    }

    // Mark successfully loaded so retries are skipped
    mlInsightsLoaded = true;
  } catch (error) {
    // Keep mlInsightsLoaded = false so user can retry by clicking the tab again
    reportUiError("ML Insights load", error, {
      target: document.getElementById("ml-eval-card"),
      message: "<p>ML data unavailable. Ensure scikit-learn is installed and the backend is running.</p>",
      mode: "html",
    });
  }
}

// Wire up the Run Evaluation button
const runEvalBtn = document.getElementById("run-eval-btn");
if (runEvalBtn) runEvalBtn.addEventListener("click", runEvaluation);

// Wire up the ML recommendation form
const mlRecForm = document.getElementById("ml-rec-form");
if (mlRecForm) {
  mlRecForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const skills = (document.getElementById("ml-skills-input")?.value || "")
      .split(/[\s,]+/).filter(Boolean);
    const goals = (document.getElementById("ml-goals-input")?.value || "")
      .split(/[\s,]+/).filter(Boolean);
    const education = document.getElementById("ml-edu-input")?.value || "";
    const limit = parseInt(document.getElementById("ml-limit-input")?.value || "10", 10);

    const payload = { education, skills, goals, limit };
    const resultsEl = document.getElementById("ml-rec-results");
    if (resultsEl) resultsEl.innerHTML = "<p>Running ML recommendations…</p>";

    try {
      const result = await fetchJSON(`${API_BASE}/api/ml-recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const recs = result.recommendations || [];
      if (!recs.length) {
        resultsEl.innerHTML = "<p>No ML matches found. Try different keywords.</p>";
        return;
      }
      resultsEl.innerHTML = recs.map(item => `
        <article class="card">
          <h3>${item.college_name}</h3>
          <p>${item.program_name}</p>
          <p class="meta">
            ML Score: <strong>${item.ml_score}</strong> •
            Cluster: ${item.ml_cluster || "—"} •
            ${formatDuration(item)}
          </p>
          ${item.ml_skills && item.ml_skills.length
            ? `<p>Key skills: ${item.ml_skills.slice(0, 6).join(", ")}</p>`
            : ""}
          ${item.details_url || item.source_url
            ? `<a href="${item.details_url || item.source_url}" target="_blank">Program details</a>`
            : ""}
        </article>
      `).join("");
    } catch (error) {
      reportUiError("ML Recommendations", error, {
        target: resultsEl,
        message: "<p>Unable to load ML recommendations. Please try again.</p>",
        mode: "html",
      });
    }
  });
}

// Load ML insights when the ML Insights nav tab is clicked (retries on failure)
let mlInsightsLoaded = false;
document.querySelectorAll(".pill-nav button").forEach(btn => {
  btn.addEventListener("click", () => {
    if (btn.dataset.target === "ml-insights" && !mlInsightsLoaded) {
      loadMlInsights();
    }
  });
});

// Also pre-load ML insights in the background shortly after page load
setTimeout(() => { if (!mlInsightsLoaded) loadMlInsights(); }, 1500);