import React, { useState, useEffect } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import "./App.css";
import prevIcon from './icons/prev.png';
import nextIcon from './icons/next.png';

const COLORS = ["#00bcd4", "#ff9800", "#4caf50", "#f44336", "#9c27b0", "#3f51b5", "#ffeb3b", "#795548"];

const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) return `${hours} hr ${minutes} min`;
  if (minutes > 0) return `${minutes} min ${secs} sec`;
  return `${secs} sec`;
};

const getFormattedDate = (date) => date.toISOString().split("T")[0];

const formatFullDate = (date) => {
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const formatTimeOnly = (date) => {
  return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
};

const App = () => {
  const [activityData, setActivityData] = useState([]);
  const [specificDate, setSpecificDate] = useState(getFormattedDate(new Date()));
  const [totalTasks, setTotalTasks] = useState(0);
  const [mostActiveHour, setMostActiveHour] = useState("");
  const [peakHour, setPeakHour] = useState("");
  const [peakActivity, setPeakActivity] = useState("");
  const [longSessions, setLongSessions] = useState([]);
  const [currentDateTime, setCurrentDateTime] = useState(new Date());

  useEffect(() => {
    if (specificDate) {
      fetchActivityData();
    }

    const interval = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, [specificDate]);

  const fetchActivityData = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/get_activity?specific_date=${specificDate}&limit=20`);
      setActivityData(response.data.activity);
      setTotalTasks(response.data.total_tasks);
      setMostActiveHour(response.data.most_active_hour);
      setPeakHour(response.data.peak_hour);
      setPeakActivity(response.data.peak_activity);
      setLongSessions(response.data.long_sessions);
    } catch (error) {
      console.error("Error fetching activity data:", error);
    }
  };

  const changeDate = (days) => {
    const currentDate = new Date(specificDate);
    currentDate.setDate(currentDate.getDate() + days);
    setSpecificDate(getFormattedDate(currentDate));
  };

  // Compute total time for percentage calculation
  const totalTime = activityData.reduce((sum, entry) => sum + entry.total_time, 0);

  return (
    <div className="container">
      <h1 className="header">User Activity Tracker</h1>

      {/* Filters Section with Current Time & Date */}
      <div className="card controls">
        <button className="nav-button" onClick={() => changeDate(-1)}>
          <img src={prevIcon} alt="Previous" />
        </button>

        <div className="date-info">
          <h3>{formatFullDate(currentDateTime)}</h3>
          <h4>{formatTimeOnly(currentDateTime)}</h4>
        </div>

        <div className="filter-item">
          <label>Select Date:</label>
          <input type="date" value={specificDate} onChange={(e) => setSpecificDate(e.target.value)} />
        </div>

        <button className="nav-button" onClick={() => changeDate(1)}>
  <img src={nextIcon} alt="Next" />
</button>

      </div>

      {/* Summary Section */}
      <div className="summary-grid">
        <div className="card total-activities">
          <h2>Total Activities</h2>
          <p>{totalTasks}</p>
        </div>

        <div className="card most-active-hour">
          <h2>Most Active Timeframe</h2>
          <p>{mostActiveHour}</p>
        </div>

        <div className="card peak-hour">
          <h2>Peak Hour Activity</h2>
          <p>{peakHour} - {peakActivity}</p>
        </div>
      </div>

      {/* Pie Chart for Percentage Breakdown */}
      <div className="card category-breakdown">
        <h2>Activity Breakdown (Percentage)</h2>
        <ResponsiveContainer width="100%" height={400}>
         <PieChart>
            <Pie
              data={activityData}
              dataKey="total_time"
              nameKey="window_title"
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={({ value }) => `${((value / totalTime) * 100).toFixed(1)}%`}
            >
              {activityData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value, name) => [`${formatTime(value)} (${((value / totalTime) * 100).toFixed(1)}%)`, name]} />
          </PieChart>
         </ResponsiveContainer>
      </div>

      {/* Long Sessions Section */}
      <div className="card long-sessions">
        <h2>Long Sessions (More than 1 Hour)</h2>
        <ul>
          {longSessions.length > 0 ? (
            longSessions.map((session, index) => (
              <li key={index}>{session.window_title} - {formatTime(session.total_time)}</li>
            ))
          ) : (
            <p>No long sessions recorded.</p>
          )}
        </ul>
      </div>
    </div>
  );
};

export default App;
