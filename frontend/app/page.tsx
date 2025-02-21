export default function Home() {
  return (
    <div className="grid grid-flow-col grid-rows-3 gap-4 h-screen">
      <div className="border row-span-3 ">01</div>
      <div className="border col-span-2 row-span-2">Messages</div>
      <div className="border col-span-2 "><input className="border" placeholder="hi"/><button className="bg-red-400">send</button></div>
    </div>
  );
}
