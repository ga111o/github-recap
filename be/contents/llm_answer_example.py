"""
prompt 

agent 1 - Codereview to add a one-line comment. Don't describe the code, tell us what's wrong with the code, what could be improved, or what was done well.

agent 2 - If the code contains a specific algorithm or difficult mechanism, provide a one-line explanation of the algorithm or mechanism used. If not, answer "None".

agent 3 - Provide a one-line overall theme.
"""

agent1_code_reviewer_example = {
  "question": """

repository: image-description-overlay

1. commit1
	- commit message: "✨ mvp done"
	- changed file: chrome-extension/background.js
		- type: added
		- content: '''
@@ -0,0 +1,8 @@
+chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
+  if (changeInfo.status === "complete" && /^http/.test(tab.url)) {
+    chrome.scripting.executeScript({
+      target: { tabId: tab.id },
+      files: ["content.js"],
+    });
+  }
+});
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,112 @@
+let debugMode = false;
+const currentUrl = window.location.href;
+let session = new Date().getTime();
+let server = "";
+
+chrome.storage.sync.get(
+  ["model", "debugMode", "server", "apiKey", "language"],
+  function (data) {
+    let model = data.model || "caption";
+    debugMode = !!data.debugMode;
+    server = data.server || "http://223.194.20.119:9919";
+    let apiKey = data.apiKey || "";
+    let language = data.language || "English";
+
+    const targetUrl = `${server}/url?url=${encodeURIComponent(
+      currentUrl
+    )}&model=${model}&session=${session}&title=${encodeURIComponent(
+      document.title
+    )}&language=${encodeURIComponent(language)}`;
+
+    if (apiKey) {
+      fetch(`${server}/apikey`, {
+        method: "POST",
+        headers: {
+          "Content-Type": "application/json",
+        },
+        body: JSON.stringify({ apiKey: apiKey, session: session }),
+      })
+        .then((response) => response.json())
+        .then((data) => {
+          if (debugMode) console.log("success - fetch api key: ", data);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch api key:", error);
+        });
+
+      fetch(targetUrl)
+        .then((response) => {
+          if (debugMode) console.log("success - fetch(targetUrl):", response);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch(targetUrl):", error);
+        });
+    }
+  }
+);
+
+async function updateImageAltText() {
+  const response = await fetch(`${server}/${session}/output`);
+  if (!response.ok) {
+    if (debugMode) console.error("failed to fetch alt texts");
+    return;
+  }
+
+  const altTexts = await response.json();
+
+  document.querySelectorAll("img").forEach((img) => {
+    const imageName = img.src.split("/").pop();
+    if (altTexts[imageName]) {
+      img.alt =
+        altTexts[imageName]["response"]["output"] ||
+        altTexts[imageName].response;
+      if (debugMode) console.log(`Alt text updated for image: ${imageName}`);
+
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log("altTexts[imageName].response");
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log(
+        "altTexts[imageName]['response']",
+        altTexts[imageName]["response"]
+      );
+      console.log(
+        "altTexts[imageName]['response']['output']",
+        altTexts[imageName]["response"]["output"]
+      );
+
+      let overlay = img.parentElement.querySelector(".image-overlay");
+      if (!overlay) {
+        overlay = document.createElement("div");
+        overlay.className = "image-overlay";
+        overlay.innerText = img.alt;
+
+        const fontSize = document.getElementById("fontSize").value || "12px";
+        overlay.style.fontSize = fontSize;
+
+        overlay.style.position = "absolute";
+        overlay.style.top = "0";
+        overlay.style.left = "0";
+        overlay.style.color = "white";
+        overlay.style.backgroundColor = "rgba(0, 0, 0, 0.65)";
+        overlay.style.backdropFilter = "blur(3px)";
+        overlay.style.padding = "5px";
+        overlay.style.pointerEvents = "none";
+        overlay.style.zIndex = "1000";
+        overlay.style.width = `${img.clientWidth}px`;
+        overlay.style.textAlign = "center";
+        overlay.style.boxSizing = "border-box";
+      }
+    }
+  });
+}
+
+setInterval(function () {
+  if (debugMode) console.log("working...");
+  if (document.readyState === "loading") {
+    document.addEventListener("DOMContentLoaded", updateImageAltText);
+  } else {
+    updateImageAltText();
+  }
+}, 5000);
+
+fetchWithUserLanguage();
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,22 @@
+{
+  "manifest_version": 3,
+  "name": "add alt",
+  "version": "1.0",
+  "permissions": ["activeTab", "scripting", "storage"],
+  "options_ui": {
+    "page": "options.html",
+    "open_in_tab": false
+  },
+  "background": {
+    "service_worker": "background.js"
+  },
+  "content_scripts": [
+    {
+      "matches": ["<all_urls>"],
+      "js": ["content.js"]
+    }
+  ],
+  "action": {
+    "default_popup": "popup.html"
+  }
+}
'''


2. commit1
	- commit message: "🐛 font size 적용 되지 않던 문제"
	- changed file: chrome-extension/content.js
		- type: modified
		- content: '''
@@ -80,9 +80,9 @@ async function updateImageAltText() {
         overlay.className = "image-overlay";
         overlay.innerText = img.alt;
 
-        const fontSize = document.getElementById("fontSize").value || "12px";
-        overlay.style.fontSize = fontSize;
-
+        // const fontSize = document.getElementById("fontSize").value || "12px";
+        // console.log(fontSize);
+        // overlay.style.fontSize = fontSize;
         overlay.style.position = "absolute";
         overlay.style.top = "0";
         overlay.style.left = "0";
@@ -95,13 +95,14 @@ async function updateImageAltText() {
         overlay.style.width = `${img.clientWidth}px`;
         overlay.style.textAlign = "center";
         overlay.style.boxSizing = "border-box";
-      }
+        overlay.style.fontSize = "13px";
 
-      const parent = img.parentElement;
-      if (parent && parent.style.position !== "relative") {
-        parent.style.position = "relative";
+        const parent = img.parentElement;
+        if (parent && parent.style.position !== "relative") {
+          parent.style.position = "relative";
+        }
+        parent.appendChild(overlay);
       }
-      parent.appendChild(overlay);
     }
   });
 }
'''

	- changed file: main/generate-alt-object.py
		- type: modified
		- content: '''
@@ -1,5 +1,4 @@
 from tools import ImageCaptionTool
-from tools import ImageCaptionTool
 from PIL import Image
 import os
 import json
'''
""",

  "answer": """
Commit 1: "✨ mvp done"

    chrome-extension/background.js

        Good: Uses chrome.tabs.onUpdated to inject the content script only when a page is fully loaded, which is efficient.

        Bad: The regex /^http/ is too broad and will match http and https URLs, but not file:// or other schemes, which might be needed.

        Improvement: Use tab.url.startsWith('http') for a more explicit and readable check for HTTP/HTTPS URLs.

    chrome-extension/content.js

        Good: Uses chrome.storage.sync to retrieve user settings, allowing for customization.

        Bad: The code is making multiple fetches to the server, which could be optimized into a single request.

        Improvement: Consolidate the API key and image description requests into a single fetch to reduce network overhead.

    chrome-extension/manifest.json

        Good: Includes necessary permissions (activeTab, scripting, storage) for the extension to function.

        Bad: The matches pattern <all_urls> is overly broad and could lead to the script running on pages where it's not needed.

        Improvement: Use a more specific matches pattern, such as http://*/* and https://*/*, to limit the scope of the content script.

Commit 2: "🐛 font size 적용 되지 않던 문제"

    chrome-extension/content.js

        Good: The fix correctly sets the overlay's position to relative on the parent element, which is necessary for absolute positioning of the overlay.

        Bad: The commented-out code for font size suggests a previous attempt that was not fully removed, which can be confusing.

        Improvement: Remove the commented-out font size code and ensure the font size is set correctly.

    main/generate-alt-object.py

        Good: Imports necessary libraries for image processing and JSON handling.

        Bad: The duplicate import of ImageCaptionTool is unnecessary and should be removed.

        Improvement: Remove the duplicate import of ImageCaptionTool.
"""
}

agent2_algorithm_explanation_example = {
  "question": """

repository: image-description-overlay

1. commit1
	- commit message: "✨ mvp done"
	- changed file: chrome-extension/background.js
		- type: added
		- content: '''
@@ -0,0 +1,8 @@
+chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
+  if (changeInfo.status === "complete" && /^http/.test(tab.url)) {
+    chrome.scripting.executeScript({
+      target: { tabId: tab.id },
+      files: ["content.js"],
+    });
+  }
+});
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,112 @@
+let debugMode = false;
+const currentUrl = window.location.href;
+let session = new Date().getTime();
+let server = "";
+
+chrome.storage.sync.get(
+  ["model", "debugMode", "server", "apiKey", "language"],
+  function (data) {
+    let model = data.model || "caption";
+    debugMode = !!data.debugMode;
+    server = data.server || "http://223.194.20.119:9919";
+    let apiKey = data.apiKey || "";
+    let language = data.language || "English";
+
+    const targetUrl = `${server}/url?url=${encodeURIComponent(
+      currentUrl
+    )}&model=${model}&session=${session}&title=${encodeURIComponent(
+      document.title
+    )}&language=${encodeURIComponent(language)}`;
+
+    if (apiKey) {
+      fetch(`${server}/apikey`, {
+        method: "POST",
+        headers: {
+          "Content-Type": "application/json",
+        },
+        body: JSON.stringify({ apiKey: apiKey, session: session }),
+      })
+        .then((response) => response.json())
+        .then((data) => {
+          if (debugMode) console.log("success - fetch api key: ", data);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch api key:", error);
+        });
+
+      fetch(targetUrl)
+        .then((response) => {
+          if (debugMode) console.log("success - fetch(targetUrl):", response);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch(targetUrl):", error);
+        });
+    }
+  }
+);
+
+async function updateImageAltText() {
+  const response = await fetch(`${server}/${session}/output`);
+  if (!response.ok) {
+    if (debugMode) console.error("failed to fetch alt texts");
+    return;
+  }
+
+  const altTexts = await response.json();
+
+  document.querySelectorAll("img").forEach((img) => {
+    const imageName = img.src.split("/").pop();
+    if (altTexts[imageName]) {
+      img.alt =
+        altTexts[imageName]["response"]["output"] ||
+        altTexts[imageName].response;
+      if (debugMode) console.log(`Alt text updated for image: ${imageName}`);
+
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log("altTexts[imageName].response");
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log(
+        "altTexts[imageName]['response']",
+        altTexts[imageName]["response"]
+      );
+      console.log(
+        "altTexts[imageName]['response']['output']",
+        altTexts[imageName]["response"]["output"]
+      );
+
+      let overlay = img.parentElement.querySelector(".image-overlay");
+      if (!overlay) {
+        overlay = document.createElement("div");
+        overlay.className = "image-overlay";
+        overlay.innerText = img.alt;
+
+        const fontSize = document.getElementById("fontSize").value || "12px";
+        overlay.style.fontSize = fontSize;
+
+        overlay.style.position = "absolute";
+        overlay.style.top = "0";
+        overlay.style.left = "0";
+        overlay.style.color = "white";
+        overlay.style.backgroundColor = "rgba(0, 0, 0, 0.65)";
+        overlay.style.backdropFilter = "blur(3px)";
+        overlay.style.padding = "5px";
+        overlay.style.pointerEvents = "none";
+        overlay.style.zIndex = "1000";
+        overlay.style.width = `${img.clientWidth}px`;
+        overlay.style.textAlign = "center";
+        overlay.style.boxSizing = "border-box";
+      }
+    }
+  });
+}
+
+setInterval(function () {
+  if (debugMode) console.log("working...");
+  if (document.readyState === "loading") {
+    document.addEventListener("DOMContentLoaded", updateImageAltText);
+  } else {
+    updateImageAltText();
+  }
+}, 5000);
+
+fetchWithUserLanguage();
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,22 @@
+{
+  "manifest_version": 3,
+  "name": "add alt",
+  "version": "1.0",
+  "permissions": ["activeTab", "scripting", "storage"],
+  "options_ui": {
+    "page": "options.html",
+    "open_in_tab": false
+  },
+  "background": {
+    "service_worker": "background.js"
+  },
+  "content_scripts": [
+    {
+      "matches": ["<all_urls>"],
+      "js": ["content.js"]
+    }
+  ],
+  "action": {
+    "default_popup": "popup.html"
+  }
+}
'''


2. commit1
	- commit message: "🐛 font size 적용 되지 않던 문제"
	- changed file: chrome-extension/content.js
		- type: modified
		- content: '''
@@ -80,9 +80,9 @@ async function updateImageAltText() {
         overlay.className = "image-overlay";
         overlay.innerText = img.alt;
 
-        const fontSize = document.getElementById("fontSize").value || "12px";
-        overlay.style.fontSize = fontSize;
-
+        // const fontSize = document.getElementById("fontSize").value || "12px";
+        // console.log(fontSize);
+        // overlay.style.fontSize = fontSize;
         overlay.style.position = "absolute";
         overlay.style.top = "0";
         overlay.style.left = "0";
@@ -95,13 +95,14 @@ async function updateImageAltText() {
         overlay.style.width = `${img.clientWidth}px`;
         overlay.style.textAlign = "center";
         overlay.style.boxSizing = "border-box";
-      }
+        overlay.style.fontSize = "13px";
 
-      const parent = img.parentElement;
-      if (parent && parent.style.position !== "relative") {
-        parent.style.position = "relative";
+        const parent = img.parentElement;
+        if (parent && parent.style.position !== "relative") {
+          parent.style.position = "relative";
+        }
+        parent.appendChild(overlay);
       }
-      parent.appendChild(overlay);
     }
   });
 }
'''

	- changed file: main/generate-alt-object.py
		- type: modified
		- content: '''
@@ -1,5 +1,4 @@
 from tools import ImageCaptionTool
-from tools import ImageCaptionTool
 from PIL import Image
 import os
 import json
'''
""",

  "answer": """
Commit 1: "✨ mvp done"

    chrome-extension/background.js

        None

    chrome-extension/content.js

        None

    chrome-extension/manifest.json

        None

        
Commit 2: "🐛 font size 적용 되지 않던 문제"

    chrome-extension/content.js

        None

    main/generate-alt-object.py

        None
"""
}

agent3_theme_provider_example = {
  "question": """

repository: image-description-overlay

1. commit1
	- commit message: "✨ mvp done"
	- changed file: chrome-extension/background.js
		- type: added
		- content: '''
@@ -0,0 +1,8 @@
+chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
+  if (changeInfo.status === "complete" && /^http/.test(tab.url)) {
+    chrome.scripting.executeScript({
+      target: { tabId: tab.id },
+      files: ["content.js"],
+    });
+  }
+});
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,112 @@
+let debugMode = false;
+const currentUrl = window.location.href;
+let session = new Date().getTime();
+let server = "";
+
+chrome.storage.sync.get(
+  ["model", "debugMode", "server", "apiKey", "language"],
+  function (data) {
+    let model = data.model || "caption";
+    debugMode = !!data.debugMode;
+    server = data.server || "http://223.194.20.119:9919";
+    let apiKey = data.apiKey || "";
+    let language = data.language || "English";
+
+    const targetUrl = `${server}/url?url=${encodeURIComponent(
+      currentUrl
+    )}&model=${model}&session=${session}&title=${encodeURIComponent(
+      document.title
+    )}&language=${encodeURIComponent(language)}`;
+
+    if (apiKey) {
+      fetch(`${server}/apikey`, {
+        method: "POST",
+        headers: {
+          "Content-Type": "application/json",
+        },
+        body: JSON.stringify({ apiKey: apiKey, session: session }),
+      })
+        .then((response) => response.json())
+        .then((data) => {
+          if (debugMode) console.log("success - fetch api key: ", data);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch api key:", error);
+        });
+
+      fetch(targetUrl)
+        .then((response) => {
+          if (debugMode) console.log("success - fetch(targetUrl):", response);
+        })
+        .catch((error) => {
+          if (debugMode) console.error("error - fetch(targetUrl):", error);
+        });
+    }
+  }
+);
+
+async function updateImageAltText() {
+  const response = await fetch(`${server}/${session}/output`);
+  if (!response.ok) {
+    if (debugMode) console.error("failed to fetch alt texts");
+    return;
+  }
+
+  const altTexts = await response.json();
+
+  document.querySelectorAll("img").forEach((img) => {
+    const imageName = img.src.split("/").pop();
+    if (altTexts[imageName]) {
+      img.alt =
+        altTexts[imageName]["response"]["output"] ||
+        altTexts[imageName].response;
+      if (debugMode) console.log(`Alt text updated for image: ${imageName}`);
+
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log("altTexts[imageName].response");
+      console.log("altTexts[imageName]", altTexts[imageName]);
+      console.log(
+        "altTexts[imageName]['response']",
+        altTexts[imageName]["response"]
+      );
+      console.log(
+        "altTexts[imageName]['response']['output']",
+        altTexts[imageName]["response"]["output"]
+      );
+
+      let overlay = img.parentElement.querySelector(".image-overlay");
+      if (!overlay) {
+        overlay = document.createElement("div");
+        overlay.className = "image-overlay";
+        overlay.innerText = img.alt;
+
+        const fontSize = document.getElementById("fontSize").value || "12px";
+        overlay.style.fontSize = fontSize;
+
+        overlay.style.position = "absolute";
+        overlay.style.top = "0";
+        overlay.style.left = "0";
+        overlay.style.color = "white";
+        overlay.style.backgroundColor = "rgba(0, 0, 0, 0.65)";
+        overlay.style.backdropFilter = "blur(3px)";
+        overlay.style.padding = "5px";
+        overlay.style.pointerEvents = "none";
+        overlay.style.zIndex = "1000";
+        overlay.style.width = `${img.clientWidth}px`;
+        overlay.style.textAlign = "center";
+        overlay.style.boxSizing = "border-box";
+      }
+    }
+  });
+}
+
+setInterval(function () {
+  if (debugMode) console.log("working...");
+  if (document.readyState === "loading") {
+    document.addEventListener("DOMContentLoaded", updateImageAltText);
+  } else {
+    updateImageAltText();
+  }
+}, 5000);
+
+fetchWithUserLanguage();
'''
	- changed file: chrome-extension/content.js
		- type: added
		- content: '''
@@ -0,0 +1,22 @@
+{
+  "manifest_version": 3,
+  "name": "add alt",
+  "version": "1.0",
+  "permissions": ["activeTab", "scripting", "storage"],
+  "options_ui": {
+    "page": "options.html",
+    "open_in_tab": false
+  },
+  "background": {
+    "service_worker": "background.js"
+  },
+  "content_scripts": [
+    {
+      "matches": ["<all_urls>"],
+      "js": ["content.js"]
+    }
+  ],
+  "action": {
+    "default_popup": "popup.html"
+  }
+}
'''


2. commit1
	- commit message: "🐛 font size 적용 되지 않던 문제"
	- changed file: chrome-extension/content.js
		- type: modified
		- content: '''
@@ -80,9 +80,9 @@ async function updateImageAltText() {
         overlay.className = "image-overlay";
         overlay.innerText = img.alt;
 
-        const fontSize = document.getElementById("fontSize").value || "12px";
-        overlay.style.fontSize = fontSize;
-
+        // const fontSize = document.getElementById("fontSize").value || "12px";
+        // console.log(fontSize);
+        // overlay.style.fontSize = fontSize;
         overlay.style.position = "absolute";
         overlay.style.top = "0";
         overlay.style.left = "0";
@@ -95,13 +95,14 @@ async function updateImageAltText() {
         overlay.style.width = `${img.clientWidth}px`;
         overlay.style.textAlign = "center";
         overlay.style.boxSizing = "border-box";
-      }
+        overlay.style.fontSize = "13px";
 
-      const parent = img.parentElement;
-      if (parent && parent.style.position !== "relative") {
-        parent.style.position = "relative";
+        const parent = img.parentElement;
+        if (parent && parent.style.position !== "relative") {
+          parent.style.position = "relative";
+        }
+        parent.appendChild(overlay);
       }
-      parent.appendChild(overlay);
     }
   });
 }
'''

	- changed file: main/generate-alt-object.py
		- type: modified
		- content: '''
@@ -1,5 +1,4 @@
 from tools import ImageCaptionTool
-from tools import ImageCaptionTool
 from PIL import Image
 import os
 import json
'''
""",

  "answer": """
Overall Theme: The primary focus of the commits was to develop a Chrome extension that automatically generates and displays alt text for images on web pages.
"""
}
