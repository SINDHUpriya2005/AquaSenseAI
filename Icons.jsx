const common = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export function IconGauge(props) {
  return (
    <svg {...common} {...props}>
      <path d="M12 3a9 9 0 1 0 9 9" />
      <path d="M12 3v3" />
      <path d="M12 12l4.2-4.2" />
      <circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconDroplet(props) {
  return (
    <svg {...common} {...props}>
      <path d="M12 2.5c3.2 4 6.5 8.1 6.5 12a6.5 6.5 0 0 1-13 0c0-3.9 3.3-8 6.5-12Z" />
    </svg>
  );
}

export function IconFlask(props) {
  return (
    <svg {...common} {...props}>
      <path d="M9 3h6" />
      <path d="M10 3v6.2L4.8 18a2 2 0 0 0 1.7 3h11a2 2 0 0 0 1.7-3L14 9.2V3" />
      <path d="M7.5 15h9" />
    </svg>
  );
}

export function IconChart(props) {
  return (
    <svg {...common} {...props}>
      <path d="M4 20V10" />
      <path d="M11 20V4" />
      <path d="M18 20v-7" />
      <path d="M3 20h18" />
    </svg>
  );
}

export function IconClock(props) {
  return (
    <svg {...common} {...props}>
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" />
    </svg>
  );
}

export function IconLogout(props) {
  return (
    <svg {...common} {...props}>
      <path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3" />
      <path d="M16 16l4-4-4-4" />
      <path d="M20 12H9" />
    </svg>
  );
}

export function IconPlus(props) {
  return (
    <svg {...common} {...props}>
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  );
}

export function IconAlert(props) {
  return (
    <svg {...common} {...props}>
      <path d="M12 3 2 20h20L12 3Z" />
      <path d="M12 9.5v4.5" />
      <path d="M12 17.2h.01" />
    </svg>
  );
}

export function IconCheck(props) {
  return (
    <svg {...common} {...props}>
      <path d="M4 12.5l5 5L20 6" />
    </svg>
  );
}

export function IconChevronDown(props) {
  return (
    <svg {...common} {...props}>
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}

export function IconTrash(props) {
  return (
    <svg {...common} {...props}>
      <path d="M4 7h16" />
      <path d="M9 7V4.8A1.8 1.8 0 0 1 10.8 3h2.4A1.8 1.8 0 0 1 15 4.8V7" />
      <path d="M6.5 7l.7 12a2 2 0 0 0 2 1.9h5.6a2 2 0 0 0 2-1.9l.7-12" />
    </svg>
  );
}

export function IconWrench(props) {
  return (
    <svg {...common} {...props}>
      <path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-3 3-2.6-2.6 3-3Z" />
    </svg>
  );
}

export function IconThermometer(props) {
  return (
    <svg {...common} {...props}>
      <path d="M12 14.5V5a2 2 0 1 0-4 0v9.5a4 4 0 1 0 4 0Z" />
    </svg>
  );
}
