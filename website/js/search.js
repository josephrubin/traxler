"use strict";

const urlParams = new URLSearchParams(window.location.search);

class Frame extends React.Component {
  render() {
    return <div className="frame search_page">{this.props.children}</div>
  }
}

class SearchResult extends React.Component {
  render() {
    return (
      <a className="search_page" href={this.props.click}>
        <div className="search_result" style={{backgroundColor: this.props.color}}>
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
  componentDidMount() {
    // Fill the search bar with the query and move the cursor to the end of the text input.
    document.getElementById('search_bar').focus();
    document.getElementById('search_bar').value = urlParams.get('q');
  }

  render() {
    return (
      <div className="search_page search_bar">
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
      result_count_text: "Loading..."
    }
  }

  componentDidMount() {
    var q = urlParams.get("q")
    var token = urlParams.get("token")
    fetch("https://api.stalk.page/search/?token=" + token + "&count=0&start=0&q=" + q)
      .then(res => res.json())
      .then(res => {
          this.setState({
            isLoaded: true,
            students: res.students,
            q: q,
            result_count_text: res.students.length +
              (res.students.length == 1 ? " Result" : " Results")
          });
        },
        error => {
          this.setState({
            isLoaded: true,
            error
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
          <div className="rule"></div>
          <SearchResult color={color} click={"student.html?!=" + student.netId + "&token=" + urlParams.get("token")}>
            <div className="peacemaker search_page">
              <h1 className="search_page">{student.name}<span style={{color: "#C7C7C7"}}> '{student.year}</span></h1>
              <Portrait src={"http://collface.deptcpanel.princeton.edu/img/" + student.image} />
            </div>
            <h2 className="search_page">{(student.study == "Computer Science" ? student.degree + " " : "") + student.study}</h2>
          </SearchResult>
        </div>
      )
      }
      )

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