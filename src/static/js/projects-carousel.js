document.addEventListener("DOMContentLoaded", () => {
  const carousel = document.querySelector(".projects-carousel");

  if (!carousel || carousel.children.length < 2) return;

  const originalCards = Array.from(carousel.children);

  const cloneCard = (card, inert) => {
    const clone = card.cloneNode(true);
    clone.removeAttribute("id");

    if (inert) {
      clone.setAttribute("aria-hidden", "true");
      clone
        .querySelectorAll("a, button, input, select, textarea")
        .forEach((element) => {
          element.setAttribute("tabindex", "-1");
        });
    }

    return clone;
  };

  const createSet = (cards, { clone = false, inert = false } = {}) => {
    const set = document.createElement("div");
    set.className = "projects-carousel__set";
    set.setAttribute("role", "presentation");

    Object.assign(set.style, {
      display: "grid",
      gridAutoFlow: "column",
      gridTemplateRows: "repeat(2, var(--project-card-height))",
      gridAutoColumns: "var(--project-card-width)",
      columnGap: "var(--project-card-gap)",
      rowGap: "var(--project-card-gap)",
      alignItems: "start",
      flex: "0 0 auto",
    });

    cards.forEach((card) => {
      set.append(clone ? cloneCard(card, inert) : card);
    });

    return set;
  };

  const leadingSet = createSet(originalCards, { clone: true, inert: true });
  const trailingSet = createSet(originalCards, { clone: true, inert: true });
  const originalSet = createSet(originalCards);

  Object.assign(carousel.style, {
    display: "flex",
    flexDirection: "row",
    flexWrap: "nowrap",
    alignItems: "start",
    columnGap: "var(--project-card-gap)",
    position: "relative",
    scrollBehavior: "auto",
    scrollSnapType: "none",
    overflowAnchor: "none",
  });

  carousel.replaceChildren(leadingSet, originalSet, trailingSet);

  const sets = [leadingSet, originalSet, trailingSet];
  let originalStart = 0;
  let originalWidth = 0;
  let position = 0;
  let currentSpeed = 0;
  let ignoreScroll = false;
  let isHovered = false;
  let isFocused = false;
  let isDocumentVisible = !document.hidden;
  let lastFrameTime = 0;
  let animationFrameId = null;

  const cruiseSpeed = 28;
  const acceleration = 70;
  const deceleration = 90;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const contentX = (element) =>
    carousel.scrollLeft +
    element.getBoundingClientRect().left -
    carousel.getBoundingClientRect().left;

  const measure = () => {
    originalStart = contentX(sets[1]);
    originalWidth = contentX(sets[2]) - originalStart;
  };

  const applyPosition = () => {
    ignoreScroll = true;
    carousel.scrollLeft = position;
    ignoreScroll = false;
  };

  const wrapPosition = () => {
    if (!originalWidth) return;

    const offset = position - originalStart;
    position =
      originalStart +
      (offset - originalWidth * Math.floor(offset / originalWidth));
  };

  const centreOriginals = () => {
    measure();
    position = originalStart;
    applyPosition();
  };

  const wantsAutoscroll = () =>
    Boolean(originalWidth) &&
    !isHovered &&
    !isFocused &&
    isDocumentVisible &&
    !reducedMotion.matches;

  const animate = (timestamp) => {
    if (!lastFrameTime) lastFrameTime = timestamp;

    const elapsedSeconds = Math.min((timestamp - lastFrameTime) / 1000, 0.064);
    lastFrameTime = timestamp;

    const targetSpeed = wantsAutoscroll() ? cruiseSpeed : 0;

    if (currentSpeed < targetSpeed) {
      currentSpeed = Math.min(
        targetSpeed,
        currentSpeed + acceleration * elapsedSeconds,
      );
    } else if (currentSpeed > targetSpeed) {
      currentSpeed = Math.max(
        targetSpeed,
        currentSpeed - deceleration * elapsedSeconds,
      );
    }

    if (currentSpeed > 0) {
      position += currentSpeed * elapsedSeconds;
      wrapPosition();
      applyPosition();
    }

    animationFrameId = requestAnimationFrame(animate);
  };

  carousel.addEventListener(
    "scroll",
    () => {
      if (ignoreScroll) return;

      position = carousel.scrollLeft;
      wrapPosition();

      if (Math.abs(carousel.scrollLeft - position) > 0.5) {
        applyPosition();
      }
    },
    { passive: true },
  );

  carousel.addEventListener("pointerenter", () => {
    isHovered = true;
  });

  carousel.addEventListener("pointerleave", () => {
    isHovered = false;
  });

  carousel.addEventListener("focusin", () => {
    isFocused = true;
  });

  carousel.addEventListener("focusout", (event) => {
    if (!carousel.contains(event.relatedTarget)) {
      isFocused = false;
    }
  });

  document.addEventListener("visibilitychange", () => {
    isDocumentVisible = !document.hidden;
    lastFrameTime = performance.now();

    if (!isDocumentVisible) {
      currentSpeed = 0;
    }
  });

  reducedMotion.addEventListener("change", () => {
    lastFrameTime = performance.now();

    if (reducedMotion.matches) {
      currentSpeed = 0;
    }
  });

  window.addEventListener("resize", () => {
    const relativePosition = originalWidth
      ? (carousel.scrollLeft - originalStart) / originalWidth
      : 0;

    measure();
    position = originalStart + relativePosition * originalWidth;
    wrapPosition();
    applyPosition();
  });

  const start = () => {
    centreOriginals();
    lastFrameTime = performance.now();

    if (!animationFrameId) {
      animationFrameId = requestAnimationFrame(animate);
    }
  };

  requestAnimationFrame(start);

  if (document.fonts?.ready) {
    document.fonts.ready.then(() => {
      const relativePosition = originalWidth
        ? (position - originalStart) / originalWidth
        : 0;
      measure();
      position = originalStart + relativePosition * originalWidth;
      wrapPosition();
      applyPosition();
    });
  }

  window.addEventListener("beforeunload", () => {
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
  });
});
