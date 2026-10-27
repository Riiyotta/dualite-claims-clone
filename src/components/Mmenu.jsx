export default function Mmenu() {
  return (
    <>
<div className={"mmenu"} id={"mmenu"} data-theme={"dark"} aria-hidden={"true"}>{" "}<nav className={"mmenu__links"} aria-label={"Mobile"}>{" "}<a href={"#movement"}><span>01</span>How it works</a>{" "}<a href={"#platform"}><span>02</span>Platform</a>{" "}<a href={"#results"}><span>03</span>Results</a>{" "}<a href={"#trust"}><span>04</span>Trust</a>{" "}<a href={"#faq"}><span>05</span>FAQ</a>{" "}<a href={"/blog/"}><span>06</span>Blog</a>{" "}</nav>{" "}<div className={"mmenu__foot"}>{" "}<a href={"#demo"} className={"btn btn--lime"}><span className={"roll"}><span>Book a 30-minute demo</span></span></a>{" "}<a href={"mailto:info@dualite.dev"} className={"micro"}>info@dualite.dev</a>{" "}</div>{" "}</div>
    </>
  );
}
