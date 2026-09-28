// ComicCraft Frontend Interactions
document.addEventListener("DOMContentLoaded", () => {
  // Preset story chip quick-fill
  const presetChips = document.querySelectorAll(".preset-chip");
  const promptInput = document.getElementById("story_prompt");
  const charInput = document.getElementById("character_name");
  const settingSelect = document.getElementById("setting");
  const toneSelect = document.getElementById("tone");
  const styleSelect = document.getElementById("art_style");

  presetChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      const char = chip.getAttribute("data-char");
      const setting = chip.getAttribute("data-setting");
      const tone = chip.getAttribute("data-tone");
      const style = chip.getAttribute("data-style");

      if (prompt && promptInput) promptInput.value = prompt;
      if (char && charInput) charInput.value = char;
      if (setting && settingSelect) settingSelect.value = setting;
      if (tone && toneSelect) toneSelect.value = tone;
      if (style && styleSelect) styleSelect.value = style;

      // Pulse feedback
      chip.style.transform = "scale(0.95)";
      setTimeout(() => {
        chip.style.transform = "";
      }, 150);
    });
  });

  // Craft Form Submit Loading Orchestration
  const craftForm = document.getElementById("comic-craft-form");
  const loadingOverlay = document.getElementById("loading-overlay");

  if (craftForm && loadingOverlay) {
    craftForm.addEventListener("submit", (e) => {
      // Validate inputs
      if (!promptInput.value.trim() || !charInput.value.trim()) {
        return;
      }

      loadingOverlay.style.display = "flex";

      const step1 = document.getElementById("step-outline");
      const step2 = document.getElementById("step-story");
      const step3 = document.getElementById("step-images");
      const step4 = document.getElementById("step-pdf");

      // Progress animation timeline
      setTimeout(() => {
        if (step1) {
          step1.classList.remove("active");
          step1.classList.add("done");
          step1.innerHTML = "<span>✓</span> 1. 5-Panel Story Outlined (Gemini Flash)";
        }
        if (step2) {
          step2.classList.add("active");
        }
      }, 2500);

      setTimeout(() => {
        if (step2) {
          step2.classList.remove("active");
          step2.classList.add("done");
          step2.innerHTML = "<span>✓</span> 2. Dialogue & Narration Crafted (Gemini Pro)";
        }
        if (step3) {
          step3.classList.add("active");
        }
      }, 5500);

      setTimeout(() => {
        if (step3) {
          step3.classList.remove("active");
          step3.classList.add("done");
          step3.innerHTML = "<span>✓</span> 3. Comic Illustrations Rendered (Stable Diffusion)";
        }
        if (step4) {
          step4.classList.add("active");
        }
      }, 9500);
    });
  }

  // Handle PDF Download Click to open / redirect to export-success page
  const downloadBtn = document.getElementById("download-pdf-btn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", () => {
      const pdfUrl = downloadBtn.getAttribute("data-pdf-url");
      const pdfFilename = downloadBtn.getAttribute("data-pdf-filename");
      const comicTitle = downloadBtn.getAttribute("data-comic-title") || "Your Comic";

      // Trigger file download
      if (pdfUrl) {
        const link = document.createElement("a");
        link.href = pdfUrl;
        link.download = pdfFilename || "comic.pdf";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }

      // Redirect user to export-success page after brief moment as requested in Scenario 3
      setTimeout(() => {
        window.location.href = `/export-success?pdf_filename=${encodeURIComponent(pdfFilename)}&title=${encodeURIComponent(comicTitle)}`;
      }, 900);
    });
  }
});
