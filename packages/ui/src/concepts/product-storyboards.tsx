"use client";

import { useState } from "react";
import {
  ArrowDown, ArrowLeft, ArrowUp, Bell, CalendarDays, Check, CheckCircle2,
  ChevronDown, ChevronRight, CircleUserRound, Clock3, Crosshair, Ellipsis,
  Flame, Flag, Globe2, Home, Info, ListFilter, LockKeyhole, Mail, Medal,
  Search, Shield, ShieldCheck, Sparkles, Swords, Trophy, UserPlus, Users,
} from "../ui/product-icons";
import {
  ProductActivityEventRow,
  ProductAvatar as Avatar,
  ProductBoardStandingRow,
  ProductButton,
  ProductFriendRow,
  ProductModel as Model,
  ProductMovement,
  ProductPanel as Panel,
  ProductRankChart,
  ProductShell,
  ProductSparkline,
  ProductTabs as Tabs,
  ProductTrendChart,
  type FixtureAvatarId as AvatarId,
  type ProductPerson as Person,
} from "../patterns/product-system";
import "./product-storyboards.css";
import "./product-accessibility-overrides.css";

const people: Person[] = [
  { name: "Alex Chen", handle: "alexchen", avatar: 5, rank: 1, burn: "124.7M", week: "612.3M", change: 5, model: "GPT-5.4" },
  { name: "Maya Patel", handle: "mayapatel", avatar: 6, rank: 2, burn: "112.3M", week: "565.9M", change: 2, model: "Claude 3.7" },
  { name: "Jordan Lee", handle: "jordanlee", avatar: 3, rank: 3, burn: "105.8M", week: "539.1M", change: 4, model: "GPT-5.4" },
  { name: "Taylor Kim", handle: "taylorkim", avatar: 4, rank: 4, burn: "97.6M", week: "512.6M", change: -1, model: "Claude 3.7" },
  { name: "Riley Morgan", handle: "rileymorgan", avatar: 2, rank: 5, burn: "92.1M", week: "489.3M", change: 1, model: "GPT-5.4" },
  { name: "Devon Brooks", handle: "devonbrooks", avatar: 7, rank: 6, burn: "88.9M", week: "467.8M", change: 2, model: "Claude 3.7" },
  { name: "Vedant", handle: "vedant", avatar: 0, rank: 7, burn: "86.4M", week: "498.7M", change: 3, model: "GPT-5.4" },
  { name: "Sam Rivera", handle: "samrivera", avatar: 1, rank: 8, burn: "81.1M", week: "476.2M", change: -1, model: "GPT-5.4" },
  { name: "Jamie Wu", handle: "jamiewu", avatar: 8, rank: 9, burn: "76.2M", week: "441.6M", change: 1, model: "Claude 3.7" },
];

export function PublicProfileStoryboard() {
  return <ProductShell active="Leaderboard"><main className="vm-sb-content profile">
    <Panel className="profile-hero"><Avatar id={0} size={132} online /><div className="hero-copy"><h1>Vedant</h1><p>@vedant</p><div><span><Globe2 size={17} /> Global rank <b>#07</b></span><span className="online-dot">Online</span></div></div><div className="hero-actions"><ProductButton><UserPlus size={18} />Add friend</ProductButton><ProductButton tone="primary"><Crosshair size={18} />Add rival</ProductButton></div></Panel>
    <div className="vm-sb-grid profile-grid"><div className="vm-sb-stack">
      <Panel className="burn-card"><header><h2>Token Burn <span>(30 days)</span> <Info size={16} /></h2><div className="burn-kpis"><div><b>86.4M</b><small>Total burn</small></div><div className="vm-sb-up"><ArrowUp size={19}/>3<small>Rank movement</small></div></div></header><Tabs labels={["Today","7 days","30 days","Season"]} active="30 days" /><ProductTrendChart /></Panel>
      <Panel className="activity-card"><h2>Recent competitive activity</h2>{[
        ["Today","Overtook Sam Rivera","You passed Sam Rivera to move to #07","+3 ranks"],
        ["May 17","Reached #07","New all-time best rank","—"],
        ["May 10","Overtook Riley Morgan","You passed Riley Morgan to move to #08","+1 rank"],
        ["May 3","Joined Founders House","You now compete in the Founders House","—"],
      ].map((x,i)=><div className="timeline-row" key={x[1]}><time>{x[0]}</time><span className="event-icon">{i===1?<Trophy/>:i===3?<Home/>:<ArrowUp/>}</span><div><strong>{x[1]}</strong><small>{x[2]}</small></div><b className={x[3][0]==="+"?"vm-sb-up":""}>{x[3]}</b></div>)}</Panel>
    </div><aside className="vm-sb-stack">
      <Panel className="model-card"><h2>Model mix <Info size={15}/></h2>{[["GPT-5.4","62% of burn","53.6M"],["Claude 3.7","29% of burn","25.1M"],["Gemini 1.5 Pro","9% of burn","7.7M"]].map(x=><div className="model-row" key={x[0]}><Model name={x[0]}/><small>{x[1]}</small><b>{x[2]}</b></div>)}<footer><span>Total</span><span>100%</span><b>86.4M</b></footer></Panel>
      <Panel className="compact-card"><h2>Board memberships</h2><div className="single-row"><Home size={20}/><b>Founders House</b><span>Since May 3, 2025</span></div></Panel>
      <Panel className="compact-card"><h2>Mutual friends <span>(12)</span></h2><div className="avatar-line">{[0,6,3,4,2,1].map(x=><Avatar key={x} id={x as AvatarId} size={42}/>) }<em>+6</em></div><small>Alex Chen, Maya Patel, Jordan Lee, Taylor Kim, Riley Morgan, Sam Rivera +6</small></Panel>
      <Panel className="compact-card"><h2>Privacy &amp; evidence</h2><div className="single-row"><ShieldCheck className="green" size={28}/><div><b>Verified competitor</b><small>Evidence submitted</small></div><span>May 3, 2025</span><ChevronRight size={19}/></div><p>Profile visibility, model mix, and burn data are public.</p></Panel>
    </aside></div>
  </main></ProductShell>;
}

export function RivalComparisonStoryboard() {
  return <ProductShell active="Leaderboard"><main className="vm-sb-content rival-page">
    <div className="page-title"><ArrowLeft/><h1>Rival comparison</h1><button className="rival-select"><Avatar id={0} size={30}/><Avatar id={1} size={30}/>Vedant vs Sam Rivera<ChevronDown size={17}/></button><ProductButton tone="danger">Remove rival</ProductButton><button className="icon-only" type="button" aria-label="More rival actions"><Ellipsis aria-hidden="true"/></button></div>
    <Panel className="duel-hero"><div className="duelist"><Avatar id={0} size={96} online/><div><h2>Vedant</h2><p>#07　·　86.4M</p></div></div><div className="duel-score"><b>5.3M <span>lead</span></b><small><i/> Ahead by 6.5%</small></div><div className="duelist right"><div><h2>Sam Rivera</h2><p>#08　·　81.1M</p></div><Avatar id={1} size={96}/></div></Panel>
    <div className="vm-sb-grid rival-grid"><div className="vm-sb-stack">
      <Panel className="compare-chart"><header><h2>Token Burn <span>(30 days)</span></h2><Tabs labels={["Today","7 days","30 days","Season"]} active="30 days"/></header><div className="legend"><i/>Vedant <i className="grey"/>Sam Rivera</div><ProductTrendChart compare label="Vedant and Sam Rivera Token Burn comparison" /></Panel>
      <section className="vm-sb-panel overtakes" aria-label="Recent overtakes" tabIndex={0}><h2>Recent overtakes</h2><div className="table-head"><span>Date</span><span>Leader change</span><span>New leader</span><span>Lead after change</span><span>Notes</span></div>{[
        ["May 24, 2025","Vedant overtook Sam Rivera","Vedant","2.1M","Vedant burned 18.7M vs Sam’s 11.2M",0],
        ["May 16, 2025","Sam Rivera overtook Vedant","Sam Rivera","0.8M","Sam burned 16.3M vs Vedant’s 10.9M",1],
        ["May 11, 2025","Vedant overtook Sam Rivera","Vedant","1.3M","Vedant burned 14.6M vs Sam’s 9.8M",0],
        ["May 4, 2025","Sam Rivera overtook Vedant","Sam Rivera","0.5M","Sam burned 12.8M vs Vedant’s 11.1M",1],
        ["Apr 29, 2025","Vedant overtook Sam Rivera","Vedant","0.6M","Vedant burned 9.7M vs Sam’s 9.1M",0],
      ].map(x=><div className="overtake-row" key={String(x[0])}>{x.slice(0,2).map(y=><span key={String(y)}>{y}</span>)}<span className="person-mini"><Avatar id={x[5] as AvatarId} size={27}/>{x[2]}</span><b className={x[5]===0?"vm-sb-up":"vm-sb-down"}>{x[3]}</b><em>{x[4]}</em></div>)}<footer>View older <ChevronDown size={15}/></footer></section>
    </div><aside className="vm-sb-stack">
      <Panel className="comparison"><h2>Comparison <span><Avatar id={0} size={40}/><Avatar id={1} size={40}/></span></h2>{[["Today burn","86.4M","81.1M"],["7d burn","498.7M","476.2M"],["Active days (30d)","28","25"],["Top model","GPT-5.4","GPT-5.4"],["Current streak","14 days","7 days"],["Shared boards","3","3"]].map(x=><div className="comparison-row" key={x[0]}><span>{x[0]}</span><b>{x[1]}</b><b>{x[2]}</b></div>)}</Panel>
      <Panel className="side-list"><h2><Users size={18}/>Shared boards <a>View all</a></h2>{["#build-in-public","#ai-tools","#no-code"].map((x,i)=><div key={x}>{x}<span>{[12,24,72][i]}h ago</span></div>)}</Panel>
      <Panel className="side-list"><h2><Sparkles size={18}/>Recent activity</h2>{["Vedant burned 12.4M tokens","Sam Rivera burned 9.1M tokens","Vedant extended their streak to 14 days"].map((x,i)=><div key={x}><ProductMovement value={i===1?-1:1}/>{x}<span>{[2,3,5][i]}h ago</span></div>)}</Panel>
      <ProductButton>View Sam’s profile</ProductButton>
    </aside></div>
  </main></ProductShell>;
}

export function FriendsStoryboard() {
  const [tab,setTab]=useState("Friends");
  return <ProductShell active="Friends"><main className="vm-sb-content friends-page">
    <div className="page-title"><Users/><h1>Friends</h1><span>14 total</span><ProductButton><UserPlus size={18}/>Find people</ProductButton></div>
    <div onClick={e=>{const t=e.target as HTMLElement;if(t.tagName==="BUTTON")setTab(t.textContent||"Friends")}}><Tabs labels={["Friends","Requests (3)","Discover"]} active={tab}/></div>
    <div className="vm-sb-grid friends-grid"><Panel className="friends-table"><div className="friend-search"><Search size={18}/>Search friends</div><div className="friend-head"><span>Friend</span><span>Presence</span><span>Global rank</span><span>Burn today</span><span>Change</span><span>Top model</span><span>Shared boards</span><span>Actions</span></div><h3><i/>Active now <small>5 friends</small></h3>{people.slice(1,6).map(p=><ProductFriendRow key={p.handle} person={p} active/>)}<h3 className="offline"><i/>Offline <small>2 friends</small></h3>{people.slice(8).concat({...people[0],name:"Parker Zhao",handle:"parkerzhao",rank:10,burn:"72.4M",change:-1}).map(p=><ProductFriendRow key={p.handle} person={p}/>) }<footer>Showing 7 of 14 friends <a>View all friends</a></footer></Panel>
    <aside className="vm-sb-stack"><Panel className="request-card"><h2>Incoming requests <b>3</b><a>View all</a></h2>{[{...people[0]},{...people[5],name:"Marcus Hale",handle:"marcushale"},{...people[1],name:"Priya Shah",handle:"priyashah"}].map((p,i)=><div className="request-row" key={p.handle}><Avatar id={p.avatar} size={38}/><span><b>{p.name}</b><small>{[8,5,6][i]} mutual friends</small></span><ProductButton>Accept</ProductButton><ProductButton>Ignore</ProductButton></div>)}</Panel>
      <Panel className="watch-card"><h2>Rival watch <a>View all</a></h2>{[{...people[7],ahead:true},{...people[3],name:"Leah Carter",ahead:false}].map((p,i)=><div className="watch-row" key={p.name}><Avatar id={p.avatar} size={43}/><span><b>{p.name}</b><small>#{p.rank}</small></span><strong className={i?"vm-sb-down":""}>{i?"2.1M":"5.3M"}<small>{i?"behind":"ahead"}</small></strong><ProductSparkline down={!!i} label={`${p.name} burn trend ${i ? "falling" : "rising"}`} /></div>)}</Panel>
      <Panel className="friend-activity"><h2>Friend activity <a>View all</a></h2>{[people[2],people[1],people[4],people[8],people[5]].map((p,i)=><div key={p.handle}><Avatar id={p.avatar} size={34}/><b>{p.name}</b><span>{["overtook Taylor Kim","reached #02 globally","joined board Summer Physique Cut","joined board Skincare Stack 2025","overtook 2 players"][i]}</span><time>{["2m","12m","1h","3h","5h"][i]}</time></div>)}</Panel></aside></div>
  </main></ProductShell>;
}

export function ActivityStoryboard() {
  const events = [
    ["Sam Rivera overtook you and now leads by 1.2M","You’re #07　·　86.4M",1],
    ["You reclaimed #07","Moved up 3 spots　·　86.4M",0],
    ["Maya Patel reached #02","112.3M　·　Claude 3.7",6],
    ["Jordan Lee challenged you as a rival","Accept to start head-to-head tracking",3],
    ["You’re invited to Founders House","Elite circle　·　High signal community",5],
    ["Season 08: Momentum started","May 15 – Jun 15　·　31 days",2],
  ] as const;
  return <ProductShell active="Activity"><main className="vm-sb-content activity-page"><div className="activity-title"><h1>Activity</h1><Tabs labels={["For you","Friends","Notifications　6"]} active="For you"/></div><div className="activity-filters"><Tabs labels={["☷　All activity","⌃　Overtakes","♕　Boards","♢　Security"]} active="☷　All activity"/><button><CheckCircle2 size={18}/>Mark all as read</button></div>
    <div className="vm-sb-grid activity-grid"><Panel className="event-ledger"><h2>Today</h2>{events.map((e,i)=><ProductActivityEventRow key={e[0]} tone={`e${i}`} icon={i===0?<ArrowUp/>:i===1?<Trophy/>:i===2?<ArrowUp/>:i===3?<Swords/>:i===4?<Users/>:<Flag/>} avatar={i<5?e[2]:undefined} title={e[0]} detail={e[1]} trailing={i>=2&&i<=4?<ProductButton>{["View leaderboard","View challenge","View invite"][i-2]}</ProductButton>:<time>{i===0?"18m ago":i===1?"45m ago":"5h ago"}</time>} unread={i<2}/>)}<h2>Yesterday</h2>{[["Evidence sync completed","All sources verified　·　128 items synced"],["Sam Rivera extended lead to 1.2M","87.6M vs 86.4M"]].map((e,i)=><ProductActivityEventRow key={e[0]} compact icon={<Shield/>} avatar={i===1?1:undefined} title={e[0]} detail={e[1]} trailing={<time>Yesterday, {i?"7:18":"10:42"} PM</time>} unread/>)}<h2>This week</h2>{people.slice(8).concat({...people[3],name:"Parker Zhao"}).map((p,i)=><ProductActivityEventRow key={p.name} compact tone={i?"red":""} icon={i?<ArrowDown/>:<ArrowUp/>} avatar={p.avatar} title={`${p.name} ${i?"dropped to #11":"climbed to #09"}`} detail={i?"−2 spots　·　68.9M":"+1 spot　·　76.2M"} trailing={<time>May {i?18:19}, {i?"8:27":"11:03"} PM</time>}/>)}</Panel>
    <aside className="vm-sb-stack"><Panel className="movement-card"><h2>Your movement</h2><div className="movement-summary"><b>#07</b><span>/ Top 100</span><ProductMovement value={3}/><small>today</small></div><ProductRankChart /></Panel><Panel className="alert-card"><h2>Rival alerts <ChevronRight/></h2><div><Avatar id={1} size={48}/><span><b>Sam Rivera</b><small>Leading you by 1.2M</small></span><strong>87.6M<small>#06</small></strong></div><i/></Panel><Panel className="settings-card"><h2>Notification settings <ChevronRight/></h2>{[[Bell,"Push notifications","On"],[Mail,"Email digest","Daily"],[Shield,"Security alerts","Instant"]].map(([Icon,n,v]:any)=><div key={n}><Icon size={20}/><span>{n}</span><b>{v}</b></div>)}</Panel><Panel className="week-card"><h2>This week</h2><div>{[["12","Overtakes"],["+5","Ranks gained"],["18","Friend activity"],["7","Board events"]].map((x,i)=><span key={x[1]}><i>{i===0?<ArrowUp/>:i===1?<Sparkles/>:i===2?<Users/>:<Trophy/>}</i><b>{x[0]}</b><small>{x[1]}</small></span>)}</div></Panel></aside></div>
  </main></ProductShell>;
}
export function BoardStandingsStoryboard() {
  const boardPeople=[people[0],people[1],people[2],{...people[6],rank:4,change:2},{...people[7],rank:5},{...people[8],rank:6},{...people[0],name:"Parker Zhao",handle:"parkerzhao",rank:7,burn:"72.4M",week:"419.3M",change:-2,avatar:4 as AvatarId},{...people[4],rank:8,burn:"68.9M",week:"402.8M",change:3},{...people[5],rank:9,burn:"65.3M",week:"384.1M",change:-1},{...people[3],rank:10,burn:"59.2M",week:"351.6M",change:2}];
  return <ProductShell active="Boards"><main className="vm-sb-content board-page"><div className="breadcrumbs">Boards　/　Founders House</div><div className="vm-sb-grid board-grid"><div className="vm-sb-stack"><Panel className="board-hero"><span className="board-mark"><Home/></span><div><h1>Founders House <small><LockKeyhole size={15}/>Private board</small></h1><p><Users size={16}/>28 members　　<ShieldCheck size={16}/>Standard evidence　　<CalendarDays size={16}/>Season ends Jun 30, 2025 (40d left)</p><span>Builders competing on clean, verified agent activity.</span></div><ProductButton><Check/>Joined</ProductButton><ProductButton><UserPlus/>Invite</ProductButton><Ellipsis/></Panel><Panel className="board-table"><header><Tabs labels={["Today","7 days","Season"]} active="Today"/><span><Clock3 size={18}/>Updates every 30s</span></header><div className="board-head"><span>Rank</span><span>Member</span><span>Burn today</span><span>7d burn</span><span>Top model</span><span>Change</span></div>{boardPeople.map(p=><ProductBoardStandingRow key={p.handle} person={p} current={p.name==="Vedant"}/>)}<footer>Rankings are based on verified Token Burn. Imported data excluded.</footer></Panel></div>
    <aside className="vm-sb-stack"><Panel className="standing-card"><h2>Your standing</h2><div><strong>#04</strong><span><b>86.4M</b><small>Burn today</small></span><span><ProductMovement value={2}/><small>vs yesterday</small></span></div><footer>Behind #03 by <b>19.4M</b></footer></Panel><Panel className="rules-card"><h2>Board rules</h2>{[[Flame,"Ranking metric","Token Burn"],[ListFilter,"Imported data","Excluded"],[Shield,"Evidence standard","Standard"],[Clock3,"Resets","Daily"]].map(([Icon,n,v]:any)=><div key={n}><Icon size={19}/><span>{n}</span><b>{v}</b></div>)}</Panel><Panel className="members-card"><h2>Members <span>(28)</span></h2><div className="avatar-line">{people.slice(0,7).map(p=><Avatar key={p.handle} id={p.avatar} size={40}/>)}<em>+21</em></div><p><Medal size={16}/>Owners　　Alex Chen, Maya Patel</p><p><Shield size={16}/>Moderators　 Jordan Lee, Sam Rivera</p></Panel><Panel className="board-activity"><h2>Recent board activity</h2>{["Chris Park joined the board","Riley Morgan overtook Devon Brooks","Jamie Wu overtook Parker Zhao"].map((x,i)=><div key={x}>{i===0?<Users/>:<ArrowUp/>}<span>{x}</span><time>{[2,5,7][i]}h ago</time></div>)}<ProductButton>View all members</ProductButton></Panel></aside></div></main></ProductShell>;
}
