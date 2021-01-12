"use strict";

const urlParams = new URLSearchParams(window.location.search);

function showShareMenu(e) {
  document.getElementById('shareMenu').style.visibility = "visible";
  document.getElementById('shareMenu').style.opacity = "1";
  // Stop the click event from closing the menu immediately.
  e.stopPropagation()
}

function hideShareMenu(e) {
  document.getElementById('shareMenu').style.visibility = "hidden";
  document.getElementById('shareMenu').style.opacity = "0";
}

function navigatorShare(e, name) {
  navigator.share({
    title: 'Nassau Network',
    text: "Check out " + name + "'s profile.",
    url: location.href + "&ref=share",
  })
  hideShareMenu();
}

var t = null;

function navigatorClip(e) {
  document.getElementById('clip').style.display = "inline";
  document.getElementById('clip').value = location.href + "&ref=copy";
  document.getElementById('clip').select();
  document.execCommand('copy'); 
  document.getElementById('clip').style.display = "none";
  hideShareMenu();
  e.stopPropagation()
  if (t != null) {
    clearTimeout(t)
  }
  document.getElementById('share_bubble_img').src = "icon/check.png"
  t = setTimeout(function() {
    document.getElementById('share_bubble_img').src = "icon/share.png"
  }, 1000)
}

function navigatorBack(e, goHome) {
  if (goHome) {
    window.location.href = "/";
  }
  else {
    window.history.back()
  }
}

class Frame extends React.Component {
  render() {
    return <div className="frame student_page"
      onClick={hideShareMenu}
      style={{"backgroundColor": this.props.color}}>{this.props.children}</div>
  }
}

class ShareBubble extends React.Component {
  render() {
    return (
      <div className={"bubblebutton share " + this.props.xtra} onClick={showShareMenu}>
        <img id="share_bubble_img" className={"icon " + this.props.xxtra} src={this.props.src} />
      </div>
    )
  }
}

class BackBubble extends React.Component {
  render() {
    return (
      <div className={"bubblebutton back " + this.props.xtra} onClick={(e) => navigatorBack(e, this.props.goHome)}>
        <img className={"icon back " + this.props.xxtra} src={this.props.src} />
      </div>
    )
  }
}

class SearchBar extends React.Component {
  focusMe() {
    document.getElementById('search_bar').focus();
  }

  render() {
    return (
      <div className="student_page search_bar" onClick={this.focusMe}>
        <img className={"icon search " + this.props.xxtra} src="icon/search.png" />
        <form className="form" method="GET" action="/search.html">
          <input id="search_bar" name="q" className="search student_page" defaultValue={this.props.fill} />
          <input type="submit" />
        </form>
      </div>
    )
  }
}

class ShareMenu extends React.Component {
  render() {
    var navShare = ""
    var shareItemClass = "share_menu_item"
    if (navigator.share) {
      shareItemClass = "share_menu_item_constricted"
      navShare = (
        <div className={"share " + shareItemClass} onClick={(e) => navigatorShare(e, this.props.name)}>
          <span>Share</span>
          <img className="share_icon" src="icon/forward.png" />
        </div>
      )
    }
    return (
      <div id="shareMenu" className="student_page share_menu">
        {navShare}
        <div className={"copy " + shareItemClass} onClick={navigatorClip}>
          <span>Copy Link</span>
          <img className="share_icon" src="icon/copy.png" />
        </div>
      </div>
    )
  }
}

class Portrait extends React.Component {
  render() {
    return (
      <img className="portrait student_page" src={this.props.src} />
    )
  }
}

class Inbar extends React.Component {
  render() {
    return (
      <div className="inbar student_page" >
        <img className="icon_small" src={this.props.src} />
        <span className="alongside_icon_small">{this.props.text}</span>
      </div>
    )
  }
}

class InbarLink extends React.Component {
  render() {
    return (
      <div className="inbar student_page" >
        <img className="icon_small" src={this.props.src} />
        <a className="alongside_icon_small" href={"mailto:" + this.props.text}>{this.props.text}</a>
      </div>
    )
  }
}

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      student: {
        name: null,
        study: null,
        email: null,
        college: null,
        degree: null,
        home: null,
        isLoaded: false
      }
    }
  }

  componentDidMount() {
    fetch("https://" + apiDomain + "/students/" + urlParams.get('!'), {
      credentials: 'include'
    })
      .then(res => {
          if (res.status == 403) {
            window.location.href = "https://" + websiteDomain + "/login.html?ref=" + window.location.href;
            return;
          }
          return res.json()
      })
      .then(res => {
          var color = "#ffffff"
          switch (Number(res.student.year)) {
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

          document.body.style.backgroundColor = color;

          if (res.student.study == "Woodrow Wilson School") {
            res.student.study = "Public and International Affairs"
          }

          this.setState({
            isLoaded: true,
            student: res.student,
            color: color,
            error: false
          });
        },
        er => {
          console.log(er)
          this.setState({
            isLoaded: true,
            error: true
          });
        }
      )
  }

  render() {
    var backBubble;
    if (urlParams.get("ref") && urlParams.get("ref") == "share" || urlParams.get("ref") == "copy")
    {
      backBubble = (
        <BackBubble goHome={true} src="icon/home.png" />
      )
    }
    else {
      backBubble = (
        <BackBubble goHome={false} src="icon/back.png" />
      )
    }
    var header = (
      <div className="peacemaker student_page">
        {backBubble}
        <SearchBar fill={this.state.student.netId} />
        <ShareBubble name={this.state.student.name} src="icon/share.png" xtra="fr" />
        <ShareMenu name={this.state.student.name} />
      </div>
    );
    var body = (
      <>
        <br />
      </>
    );
    if (this.state.isLoaded) {
      if (this.state.error) {
        body = (
          <>
            <br />
            <br />
            <h2>We're Sorry</h2>
            <br />
            <span>The server encounter an error. Please try refreshing the page. We apologize for the inconvenience.</span>
          </>
        )
      }
      else {
        body = (
          <>
            <Portrait src={"/large/" + this.state.student.image} />

            <div className="student_page spacer_one"></div>

            <h1 className="student_page">{this.state.student.name}</h1>
            <h2 className="student_page">{this.state.student.study + ", " + this.state.student.degree + " " + this.state.student.year}</h2>

            <div className="inbar_group student_page">
              <InbarLink src="icon/mail.png" text={this.state.student.netId + "@princeton.edu"} />
              <Inbar src="icon/place.png" text={this.state.student.college} />
            </div>
            <input id="clip" className="clip" />
          </>
        );
      }
    }
    return (
      <Frame color={this.state.color}>
        {header}
        {body}
      </Frame>
    )
  }
}

// <Inbar src="icon/place.png" text={this.state.student.home} />

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
