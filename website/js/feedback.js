// ==========================================================================
// Fabric Arcade — per-game Feedback & Share
// --------------------------------------------------------------------------
// SHARE buttons work out of the box (LinkedIn / X / Reddit share intents).
//
// COMMENTS use giscus (GitHub Discussions). To enable them:
//   1. Make sure the repo is public and Discussions are ON:
//      https://github.com/maenglar78/fabric-arcade/settings  → Features → Discussions
//   2. Install the giscus app on the repo: https://github.com/apps/giscus
//   3. Go to https://giscus.app , enter repo "maenglar78/fabric-arcade",
//      choose Mapping = "pathname", pick a Discussion category (e.g. "Game Feedback").
//   4. Copy the generated data-repo-id and data-category-id below.
// Until you fill these in, a "Report a bug on GitHub" fallback link is shown.
// ==========================================================================

const GISCUS_REPO = "maenglar78/fabric-arcade";
const GISCUS_REPO_ID = "REPLACE_WITH_REPO_ID";         // <-- from giscus.app
const GISCUS_CATEGORY = "Game Feedback";
const GISCUS_CATEGORY_ID = "REPLACE_WITH_CATEGORY_ID"; // <-- from giscus.app

(function () {
  // ---- Share buttons: pre-filled post with #FabricArcade #<Game> + link ----
  const pageUrl = window.location.href;
  const h1 = document.querySelector("h1");
  const gameName = (h1 ? h1.textContent : document.title.split(/[-–—]/)[0]).trim();
  // Hashtag from the game name, e.g. "Fabric Racing Game" -> "FabricRacingGame"
  const gameTag = gameName.replace(/[^A-Za-z0-9]/g, "");
  const message =
    "Just played " + gameName +
    " on Fabric Arcade — learn Microsoft Fabric by playing! 🎮";

  const url = encodeURIComponent(pageUrl);
  const xText = encodeURIComponent(message);
  // LinkedIn ignores pre-filled text on share-offsite, so we open the composer
  // (shareActive) with the text + hashtags + link; LinkedIn builds the preview
  // from the URL contained in the text.
  const liText = encodeURIComponent(
    message + "\n\n#FabricArcade #" + gameTag + "\n" + pageUrl
  );
  // Reddit link posts only take a title (no hashtags).
  const redditTitle = encodeURIComponent(
    gameName + " — learn Microsoft Fabric by playing 🎮 (Fabric Arcade)"
  );

  const shareMap = {
    "share-linkedin": "https://www.linkedin.com/feed/?shareActive=true&text=" + liText,
    "share-x": "https://twitter.com/intent/tweet?text=" + xText + "&url=" + url + "&hashtags=FabricArcade," + gameTag,
    "share-reddit": "https://www.reddit.com/submit?url=" + url + "&title=" + redditTitle
  };
  Object.keys(shareMap).forEach(function (id) {
    const el = document.getElementById(id);
    if (el) el.setAttribute("href", shareMap[id]);
  });

  // ---- Comments (giscus) ----
  const mount = document.getElementById("comments");
  if (!mount) return;

  const configured =
    GISCUS_REPO_ID.indexOf("REPLACE") === -1 &&
    GISCUS_CATEGORY_ID.indexOf("REPLACE") === -1;

  if (configured) {
    const s = document.createElement("script");
    s.src = "https://giscus.app/client.js";
    s.setAttribute("data-repo", GISCUS_REPO);
    s.setAttribute("data-repo-id", GISCUS_REPO_ID);
    s.setAttribute("data-category", GISCUS_CATEGORY);
    s.setAttribute("data-category-id", GISCUS_CATEGORY_ID);
    s.setAttribute("data-mapping", "pathname");
    s.setAttribute("data-strict", "0");
    s.setAttribute("data-reactions-enabled", "1");
    s.setAttribute("data-emit-metadata", "0");
    s.setAttribute("data-input-position", "top");
    s.setAttribute("data-theme", "dark");
    s.setAttribute("data-lang", "en");
    s.setAttribute("crossorigin", "anonymous");
    s.async = true;
    mount.appendChild(s);
  } else {
    mount.innerHTML =
      '<p class="comments-todo">💬 Comments are being set up. In the meantime, ' +
      '<a href="https://github.com/' + GISCUS_REPO + '/issues/new?labels=feedback&title=%5BFeedback%5D%20" ' +
      'target="_blank" rel="noopener">open a GitHub issue</a> to leave feedback or report a 🐛 bug.</p>';
  }
})();
