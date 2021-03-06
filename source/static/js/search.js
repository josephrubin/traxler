"use strict";

const urlParams = new URLSearchParams(window.location.search);
const storage = window.localStorage;

function saveScroll(url) {
  scroll = document.documentElement.scrollTop;
  storage.setItem("lastScroll", scroll);
}

class Frame extends React.Component {
  render() {
    return <div className="frame search_page">{this.props.children}</div>
  }
}

class SearchResult extends React.Component {
  render() {
    return (
      /* We use href to allow middle click (open-in-new-tab) behavior. */
      <a className="search_page" onClick={saveScroll} href={this.props.click}>
        <div className={"search_result search_page " + this.props.extraClasses} style={{backgroundColor: this.props.color}}>
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
      result_count_text: "Loading...",
      show_home_link: false
    }
  }

  componentDidMount() {
    // Get the user's query.
    var q = urlParams.get("q")

    // If the query string is blank (or just spaces), don't make the API
    // request as the server will not allow that query.
    if (q.split(' ').join('') == '') {
      this.setState({
        isLoaded: true,
        students: [],
        q: q,
        result_count_text: "0 Results",
        error: false
      });
      return
    }

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
        setTimeout(function() {document.documentElement.scrollTop = storage.getItem('lastScroll')}, 5)
        return;
      }
    }

    // Cache miss.
    // We make two API calls concurrently. Load the fast data ASAP and the slow data will follow.
    this.fetchFast(q)
    this.fetchSlow(q)
  }

  fetchFast(q) {
    fetch(apiUrl + "/search/?count=0&start=0&fast=1&q=" + q, {
      credentials: 'include'
    })
      .then(res => {
          if (res.status == 403) {
            window.location.href = websiteUrl + "/login.html?ref=" + window.location.href;
            return;
          }
          return res.json()
      })
      .then(res => {
          if (res.status == 403) {
            window.location.href = websiteUrl + "/login.html?ref=" + window.location.href;
          }

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

  fetchSlow(q) {
    fetch(apiUrl + "/search/?count=0&start=0&fast=0&q=" + q, {
      credentials: 'include'
    })
    .then(res => {
        if (res.status == 403) {
          window.location.href = websiteUrl + "/login.html?ref=" + window.location.href;
          return;
        }
        return res.json()
    })
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
          show_home_link: true,
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
    var stateSave = this.state;
    let results = this.state.students.map(function(student, idx) {
      var color = "#ffffff"
      switch (Number(student.year)) {
        case 2021:
          color = "#fffef0"
          break;
        case 2022:
          color = "#dbe9ff"
          break;
        case 2023:
          color = "#ffeded"
          break;
        case 2024:
          color = "#d4ffe4"
          break;
      }

      if (student.study == "Woodrow Wilson School") {
        student.study = "Public and International Affairs"
      }

      var extraClasses = "";
      if (idx == stateSave.students.length - 1){
        extraClasses = "rb"
      }

      return (
        <div key={student.netid} className={extraClasses}>
          <SearchResult extraClasses={extraClasses} color={color} click={"student.html?!=" + student.netId}>
            <div className={"peacemaker search_page"}>
              <h1 className="search_page">{student.name}<span style={{color: "#C7C7C7"}}> '{student.year.slice(-2)}</span></h1>
              <Portrait src={student.photo_small} />
            </div>
            <h2 className="search_page">{(student.study == "Computer Science" ? student.degree + " " : "") + student.study}</h2>
          </SearchResult>
        </div>
      )
      }
      )

    if (this.state.isLoaded && this.state.error) {
      results = (
        <SearchResult extraClasses={"rb"} color={"white"} click={"https://"}>
          <h2>We're Sorry</h2>
          <br />
          <span>The server encounter an error. Please try refreshing the page. We apologize for the inconvenience.</span>
        </SearchResult>
      )
    }

    var homeLink = ""
    if (this.state.show_home_link) {
      homeLink = (
        <a href={"/"} className="home_link fr">Return home</a>
      )
    }

    return (
      <Frame>
        <div style={{paddingLeft: "18px", paddingRight: "18px"}}>
          <SearchBar fill={this.state.q} />
        </div>
        <div className="preacemaker search_page header">
          <div className="result_count">{this.state.result_count_text}</div>
          {homeLink}
        </div>
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
