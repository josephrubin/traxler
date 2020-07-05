"use strict";

const urlParams = new URLSearchParams(window.location.search);

class Frame extends React.Component {
  render() {
    return <div className="frame search_page">{this.props.children}</div>
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
           //autoFocus="autoFocus"
            />
           <input type="hidden" name="token" value={urlParams.get("token")} />
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
          title="It’s a page, for stalking!"
          body="So you probably want to bookmark this site before your friends do."
          color={color_one}
        />
        <Infobar
          title="Who are you?"
          body="You would stalk the unstalkable? The absolute madness!"
          color={color_two}
        />
        <Infobar
          title="No, seriously; I have a concern with the site"
          body={["If you want your information taken down, make sure it’s gone from the residential college facebook, then fill out ",
                  <a href="https://docs.google.com/forms/d/e/1FAIpQLSeilPyg8O-HgPPOTLzXXwPhtga40cZenhwqd7VTOfW96UthUA/viewform">this</a>, " form."]}
          color={color_three}
        />
        <Infobar
          title="Disclaimer"
          body="This site is provided for informational purposes only. Do not use this site to stalk or harrass anybody."
          color={color_four}
        />
      </Frame>
    )
  }
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);