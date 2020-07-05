"use strict";

const urlParams = new URLSearchParams(window.location.search);
const storage = window.localStorage;

function navigateStudent(e, url) {
  scroll = document.documentElement.scrollTop;
  storage.setItem("lastScroll", scroll);
  window.location.href = url;
}

class Frame extends React.Component {
  render() {
    return <div className="frame search_page">{this.props.children}</div>
  }
}

class SearchResult extends React.Component {
  render() {
    return (
      <a className="search_page" onClick={(e) => navigateStudent(e, this.props.click)}>
        <div className="search_result search_page" style={{backgroundColor: this.props.color}}>
          {this.props.children}
        </div>
      </a>
    )
  }
}

class Portrait extends React.Component {
  render() {
    return (
      <div className="fr">
        <div className={"portrait search_page " + this.props.xtra}>
          <img className="portrait search_page" src={this.props.src} />
        </div>
        <img className="portrait_icon search_page" src="icon/arrow.png" />
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

  componentDidMount() {
    // Fill the search bar with the query and move the cursor to the end of the text input.
    this.focusMe();
    document.getElementById('search_bar').value = urlParams.get('q');
  }

  render() {
    return (
      <div className="search_page search_bar" onClick={this.focusMe}>
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
  constructor(props) {
    super(props)
    this.state = {
      students: [],
      slowCompleted: false,
      result_count_text: "Loading..."
    }
  }

  componentDidMount() {
    // Get the user's query.
    var q = urlParams.get("q")

    // If this page was loaded from the browser back button
    // (or our in-app back button), we want to load the previous
    // search from the cache.
    var tryCache = true;
    if (window.performance && window.performance.getEntriesByType && window.performance.getEntriesByType('navigation')[0]) {
      // If the browser supports this API, only use the cache if the page comes from history.
      tryCache = (window.performance.getEntriesByType('navigation')[0].type == "back_forward");
      // If the browser does not support this API, use the cache either way.
    }

    if (tryCache) {
      // Check to see if the query is in the cache.
      var lastState = JSON.parse(storage.getItem('lastState'));
      if (lastState && lastState['q'] == q) {
        // Cache hit.
        this.setState(lastState);

        // Restore the last scroll (not needed for Firefox, but needed for Chrome).
        setTimeout(function() {document.documentElement.scrollTop = storage.getItem('lastScroll')}, 10)
        return;
      }
    }

    // Cache miss.
    var token = urlParams.get("token")
    // We make two API calls concurrently. Load the fast data ASAP and the slow data will follow.
    this.fetchFast(token, q)
    this.fetchSlow(token, q)
  }

  fetchFast(token, q) {
    fetch("https://api.stalk.page/search/?token=" + token + "&count=0&start=0&fast=1&q=" + q)
      .then(res => res.json())
      .then(res => {
          // If we somehow finished after the slow request, do nothing. The DOM is already populated.
          if (this.state.slowCompleted) {
            return;
          }
          storage.setItem('lastScroll', "")
          this.setState({
            isLoaded: true,
            students: res.students,
            q: q,
            result_count_text: res.students.length +
              (res.students.length == 1 ? " Result" : " Results") + " | Searching for more...",
            error: false
          });
          storage.setItem("lastState", JSON.stringify(this.state))
        },
        er => {
          this.setState({
            isLoaded: true,
            error: true
          });
        }
      )
  }

  fetchSlow(token, q) {
    fetch("https://api.stalk.page/search/?token=" + token + "&count=0&start=0&fast=0&q=" + q)
    .then(res => res.json())
    .then(res => {
        storage.setItem('lastScroll', "")
        this.setState({
          isLoaded: true,
          slowCompleted: true,
          students: res.students,
          q: q,
          result_count_text: res.students.length +
            (res.students.length == 1 ? " Result" : " Results") +
            (res.too_many_tokens ? " | Only the first four search terms are considered" : ""),
          error: false
        });
        storage.setItem("lastState", JSON.stringify(this.state))
      },
      er => {
        this.setState({
          isLoaded: true,
          error: true
        });
      }
    )
  }

  render() {
    let results = this.state.students.map(function(student) {
      var color = "#ffffff"
      switch (Number(student.year)) {
        case 21:
          color = "#fffef0"
          break;
        case 22:
          color = "#dbe9ff"
          break;
        case 23:
          color = "#ffeded"
          break;
        case 24:
          color = "#d4ffe4"
          break;
      }

      if (student.study == "Woodrow Wilson School") {
        student.study = "Public and International Affairs"
      }

      return (
        <div key={student.netId}>
          <SearchResult color={color} click={"student.html?!=" + student.netId + "&token=" + urlParams.get("token")}>
            <div className="peacemaker search_page">
              <h1 className="search_page">{student.name}<span style={{color: "#C7C7C7"}}> '{student.year}</span></h1>
              <Portrait src={"https://www.stalk.page/small/" + student.image} />
            </div>
            <h2 className="search_page">{(student.study == "Computer Science" ? student.degree + " " : "") + student.study}</h2>
          </SearchResult>
        </div>
      )
      }
      )

    if (this.state.isLoaded && this.state.error) {
      results = (
        <SearchResult color={"white"} click={"javvascript:return false;"}>
          <h2>We're Sorry</h2>
          <br />
          <span>The server encounter an error. Please try refreshing the page. We apologize for the inconvenience.</span>
        </SearchResult>
      )
    }

    return (
      <Frame>
        <div style={{paddingLeft: "18px", paddingRight: "18px"}}>
          <SearchBar fill={this.state.q} />
        </div>
        <div className="result_count">{this.state.result_count_text}</div>
        {results}
      </Frame>
    )
  }
}
//translateY(-2px)

ReactDOM.render(
  <App />,
  document.getElementById('root')
);