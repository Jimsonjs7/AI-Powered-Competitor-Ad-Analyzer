import React from "react";

interface DesignNotesProps {
  onBack: () => void;
}

export const DesignNotes: React.FC<DesignNotesProps> = ({ onBack }) => {
  const sections = [
    {
      title: "Concept",
      items: [
        {
          name: "Ad Desk, a three-pane workspace",
          desc: "Choose competitors on the left, scan their ads in the middle, decide and create on the right. The screen reads in the same order as the job: who to watch, what they run, what BrandMonk should make. Nothing opens in a new page, so context is never lost.",
        },
      ],
    },
    {
      title: "Colour",
      items: [
        {
          name: "Canvas #F6F7F5",
          desc: "A very light green-grey instead of pure white. It cuts glare during long scanning sessions and lets white panels look raised without shadows.",
          color: "#F6F7F5",
        },
        {
          name: "Surface #FFFFFF",
          desc: "Ads are judged against a neutral ground. White keeps competitor colours true, which matters when you study their palettes.",
          color: "#FFFFFF",
        },
        {
          name: "Ink #1B2421",
          desc: "A tinted dark with about 15 to 1 contrast on white. It is softer than pure black and still passes the strictest accessibility level.",
          color: "#1B2421",
        },
        {
          name: "Muted #5E6A66",
          desc: "Secondary text at roughly 5.6 to 1 contrast, which passes AA, so small labels stay readable on a phone in daylight.",
          color: "#5E6A66",
        },
        {
          name: "Accent teal #0A7C6E",
          desc: "Meta’s own interface is blue, so a teal tool is never mistaken for the platform whose ads we study. Teal also reads as growth and go, which fits a marketing academy. It is used only for selection, the main action and scores, so the eye learns that teal means act here.",
          color: "#0A7C6E",
        },
        {
          name: "Amber #9A5A08",
          desc: "Reserved for cautions such as a competitor that needs review. It is always paired with a text label, so meaning never depends on colour alone.",
          color: "#9A5A08",
        },
        {
          name: "Brand kit kept separate",
          desc: "The poster preview uses BrandMonk’s navy, blue and sun, not the tool’s teal, so the tool’s chrome never tints the result you will publish.",
          color: "#16202E",
        },
        {
          name: "Avoided: gradients and dark mode",
          desc: "Gradients add noise that competes with the ads. Dark mode misjudges ad colours, and posters are seen in daylight, so it can wait.",
        },
      ],
    },
    {
      title: "Typography",
      items: [
        {
          name: "Public Sans, one family",
          desc: "Designed for readability with open letter shapes. Its digits are tabular, so days and scores line up. One family keeps the interface neutral, so the ads supply the personality, and it loads faster than two fonts.",
        },
        {
          name: "Scale 13, 15, 18, 24",
          desc: "Roughly a 1.2 step. Labels are 13, body 15, titles 18, page title 24, and only three weights (400, 600, 700) are used so hierarchy is clear without clutter.",
        },
        {
          name: "Sentence case, no all caps",
          desc: "Mixed case is faster to read. Lines in the detail pane stay under 65 characters for comfortable reading.",
        },
      ],
    },
    {
      title: "Layout and flow",
      items: [
        {
          name: "Ads are the hero",
          desc: "The ad wall gets all remaining width, and the surrounding chrome stays narrow. Tiles use the 4 to 5 ratio of Instagram feed ads, so each creative is seen the way its audience sees it.",
        },
        {
          name: "Longest running first",
          desc: "An advertiser stops paying for ads that do not work, so running time is the best free performance signal. Each tile shows a run-length bar, so you see it without reading.",
        },
        {
          name: "Persistent detail pane",
          desc: "Studying ads means opening many in a row. A pop-up costs two clicks per ad, a pane costs one. Arrow keys or J and K also move through ads.",
        },
        {
          name: "Verdict first, evidence next",
          desc: "The score and one-line reason come before the breakdown. People decide first and check details second.",
        },
      ],
    },
    {
      title: "Writing and accessibility",
      items: [
        {
          name: "Plain, outcome-led labels",
          desc: "Buttons say what happens, such as Create BrandMonk poster from this ad. Empty states say what to try next.",
        },
        {
          name: "No emoji",
          desc: "They render differently on each device and read as casual. Text and consistent shapes are clearer and work well with screen readers.",
        },
        {
          name: "Accessible by default",
          desc: "Visible 2px teal focus ring, full keyboard use, labelled controls, pressed and selected states announced, reduced motion respected, and tap targets of 34px or more.",
        },
      ],
    },
  ];

  return (
    <div className="nv">
      <div>
        <h1>Design notes</h1>
        <p>
          Every choice in Ad Desk has a reason tied to the job: finding what competitors run and turning it into a better poster. This page lists each decision and why.
        </p>

        {sections.map((sec) => (
          <section key={sec.title}>
            <h2>{sec.title}</h2>
            {sec.items.map((item) => (
              <div key={item.name} className="rw">
                <b>
                  {item.color && (
                    <span className="sw" style={{ background: item.color }}></span>
                  )}
                  {item.name}
                </b>
                <p>{item.desc}</p>
              </div>
            ))}
          </section>
        ))}

        <button className="btn pri" style={{ marginTop: "20px" }} onClick={onBack}>
          Back to workspace
        </button>
      </div>
    </div>
  );
};
