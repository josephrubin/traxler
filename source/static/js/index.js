"use strict";

const urlParams = new URLSearchParams(window.location.search);

class Frame extends React.Component {
  render() {
    return <div className="frame index_page">{this.props.children}</div>
  }
}

class Infobar extends React.Component {
  render() {
    return (
      <div className="search_result" style={{backgroundColor: this.props.color}}>
        <h1 className="index_page">{this.props.title}</h1>
        <h2 className="index_page">{this.props.body}</h2>
      </div>
    )
  }
}

class SearchBar extends React.Component {
  focusMe() {
    document.getElementById('search_bar').focus();
  }

  componentDidMount() {
    this.focusMe();
  }

  render() {
    return (
      <div className="index_page search_bar" onClick={this.focusMe}>
        <img className={"icon search " + this.props.xxtra} src="icon/search.png" />
        <form className="form" method="GET" action="/search.html">
          <input id="search_bar" name="q" className="search"
            placeholder="Search by name or netid"
           //autoFocus="autoFocus"
            />
          <input type="submit" />
        </form>
      </div>
    )
  }
}

class App extends React.Component {
  render() {
    var color_one = "#fffef0"
    var color_two = "#dbe9ff"
    var color_three = "#ffeded"
    var color_four = "#d4ffe4"

    return (
      <Frame>
        <div style={{paddingLeft: "18px", paddingRight: "18px"}}>
          <SearchBar fill={""} />
        </div>
        <div className="rule"></div>
        <Infobar
          key="1"
          title="Welcome! We're glad you made it."
          body="This website lets you find fellow Princeton undergrads. Just use the bar above to search."
          color={color_four}
        />
        <Infobar
          key="2"
          title="What can I search for?"
          body="It's best if you start with a name. If you're not sure about the spelling, try using full names. We'll do our best from there."
          color={color_two}
        />
        <Infobar
          key="3"
          title="What's with the design of this website?"
          body={[
            "Errr.... ",
            "You may have heard of mobile-first design. ",
            "This is a new thing that we like to call mobile-last design. ",
            "It's when you try mobile-first and then never make the desktop design. ",
            "Users have described it as ", <i>sleek</i>, "."
          ]}
          color={color_one}
        />
        <Infobar
          key="4"
          title="Information"
          body="This site uses cookies to keep you logged in and speed up navigation. By using this site you agree to have cookies stored on your device."
          color={color_two}
        />
        <Infobar
          key="5"
          title="Policies"
          body="This site is provided for informational purposes only. Do not use this site to stalk or harrass anybody."
          color={color_four}
        />
        <Infobar
          key="6"
          title="I have a concern with the site"
          body={["We're sorry to hear it. If you want your information taken down, make sure it’s gone from the residential college facebook, then fill out ",
                  <a href="https://docs.google.com/forms/d/e/1FAIpQLSeilPyg8O-HgPPOTLzXXwPhtga40cZenhwqd7VTOfW96UthUA/viewform">this form</a>, "."]}
          color={color_three}
        />
        <Infobar
          key="7"
          title="I have a correction to make to your search results"
          body={["If you think our search results could be improved, please fill out ",
                  <a href="https://docs.google.com/forms/d/e/1FAIpQLSc1n9raVxDINjtMTzovnwBHEe3BtG58Z7u-XvFy7KGBLAfxcg/viewform">this form</a>, "."]}
          color={color_one}
        />
      </Frame>
    )
  }
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);