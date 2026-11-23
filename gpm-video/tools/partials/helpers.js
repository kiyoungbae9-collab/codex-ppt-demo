    // Shared motion vocabulary (SPEC.md MOTION). `tl` is this scene's paused timeline.
    const TEAL = "#008C91", LIGHT = "#E4F2F1", HAIR = "#D3DDDE", WHITE = "#FFFFFF";
    const E = {
      // text and blocks arrive by focusing in place: blur 8 -> 0, no translate
      blurIn: (sel, t, d = 0.45) =>
        tl.fromTo(sel, { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: d, ease: "expo.out" }, t),
      // title words: 0.13 s each, 0.067 s apart
      words: (sel, t) =>
        tl.fromTo(sel, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.13, stagger: 0.067, ease: "power4.out" }, t),
      // lines and arrows draw
      drawX: (sel, t, d = 0.6, origin = "left center") =>
        tl.fromTo(sel, { scaleX: 0, transformOrigin: origin }, { scaleX: 1, duration: d, ease: "power2.inOut" }, t),
      drawY: (sel, t, d = 0.45, origin = "center top") =>
        tl.fromTo(sel, { scaleY: 0, transformOrigin: origin }, { scaleY: 1, duration: d, ease: "power2.inOut" }, t),
      // SVG strokes draw (pathLength="1" on the element)
      stroke: (sel, t, d = 0.7) =>
        tl.fromTo(sel, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: d, ease: "power2.inOut" }, t),
      // cards open left to right
      open: (sel, t, d = 0.5) =>
        tl.fromTo(sel, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: d, ease: "power3.out" }, t),
      // tags, ticks and stamps land with a damped spring (scale only; opacity never overshoots)
      land: (sel, t) => {
        tl.fromTo(sel, { scale: 0.86 }, { scale: 1, duration: 0.4, ease: "back.out(1.5)" }, t);
        tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.18, ease: "power2.out" }, t);
      },
      // focus: the named item goes teal, the rest step back
      on: (sel, t) => tl.to(sel, { opacity: 1, borderColor: TEAL, backgroundColor: LIGHT, duration: 0.3, ease: "power2.inOut" }, t),
      off: (sel, t, dimTo = 0.38) => tl.to(sel, { opacity: dimTo, borderColor: HAIR, backgroundColor: WHITE, duration: 0.3, ease: "power2.inOut" }, t),
      rest: (sel, t) => tl.to(sel, { opacity: 1, borderColor: HAIR, backgroundColor: WHITE, duration: 0.4, ease: "power2.inOut" }, t),
      dim: (sel, t, v = 0.38) => tl.to(sel, { opacity: v, duration: 0.3, ease: "power2.inOut" }, t),
      full: (sel, t) => tl.to(sel, { opacity: 1, duration: 0.3, ease: "power2.inOut" }, t),
      ink: (sel, t, c = "#005B62") => tl.to(sel, { color: c, duration: 0.35, ease: "power2.inOut" }, t),
      // the scene leaves as one: blur out and fade, ending one frame before the cut
      exit: (t) => tl.to("#{{ID}}-stage", { opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power3.in" }, t),
      title: () => {
        E.words("#{{ID}}-title .w", 0.25);
        E.drawX("#{{ID}}-rule", 0.55, 0.5);
        E.blurIn("#{{ID}}-page", 0.3, 0.4);
      },
    };
    // focus one id from a list of already-visible ids
    const focus = (ids, active, t) => ids.forEach((id) => (id === active ? E.on(id, t) : E.off(id, t)));
