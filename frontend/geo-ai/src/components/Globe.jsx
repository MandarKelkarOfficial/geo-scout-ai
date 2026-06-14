// components/Globe.jsx
export default function Globe() {
  return (
    <div className="css-globe-container">
      <div className="css-globe">
        <div className="css-globe__continents" />
        <div className="css-globe__grid">
          <div className="css-globe__lat" />
          <div className="css-globe__long css-globe__long--1" />
          <div className="css-globe__long css-globe__long--2" />
        </div>
      </div>
    </div>
  );
}