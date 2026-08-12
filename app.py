import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Development of a Healthcare Operations Intelligence Dashboard with Decision Analytics",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Operations Dashboard")
st.caption("Interactive operational dashboard built with Streamlit + Plotly")


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def first_existing(df, names):
    for name in names:
        if name in df.columns:
            return name
    return None


def safe_mean(df, col):
    return df[col].mean() if col and col in df.columns else None


def money(value):
    return f"₹{value:,.0f}" if pd.notna(value) else "N/A"


# ---------------------------------------------------------
# DATA UPLOAD
# ---------------------------------------------------------
st.sidebar.header("📁 Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload your hospital CSV",
    type=["csv"]
)

if uploaded_file is None:
    st.info(
        "Upload the master hospital CSV to start. "
        "The dashboard is designed for columns such as "
        "Patient_ID, Department_Patient/Department, Admit_Date/Admission_Date, "
        "Wait_Time_Minutes, Length_of_Stay_Days, Doctor_Name, Hospital_Name, "
        "Hospital_Type, Total_Beds, Doctor_ID, Nurse_ID and Treatment_Cost_INR."
    )
    st.stop()


df = pd.read_csv(uploaded_file)


# ---------------------------------------------------------
# COLUMN DETECTION
# ---------------------------------------------------------
patient_col = first_existing(
    df,
    ["Patient_ID", "PatientId", "PatientID"]
)

dept_col = first_existing(
    df,
    ["Department_Patient", "Department"]
)

date_col = first_existing(
    df,
    ["Admission_Date", "Admit_Date", "Admission Date", "Admit Date"]
)

discharge_col = first_existing(
    df,
    ["Discharge_Date", "Discharge_Time", "Discharge Date"]
)

wait_col = first_existing(
    df,
    ["Wait_Time_Minutes", "Wait_Time", "Waiting_Time_Minutes"]
)

los_col = first_existing(
    df,
    ["Length_of_Stay_Days", "Length_of_Stay", "LOS_Days"]
)

doctor_col = first_existing(
    df,
    ["Doctor_Name", "Doctor"]
)

doctor_id_col = first_existing(
    df,
    ["Doctor_ID", "DoctorId", "DoctorID"]
)

nurse_id_col = first_existing(
    df,
    ["Nurse_ID", "NurseId", "NurseID"]
)

diagnosis_col = first_existing(
    df,
    ["Diagnosis"]
)

cost_col = first_existing(
    df,
    ["Treatment_Cost_INR", "Treatment_Cost_USD",
     "Treatment_Cost", "Cost"]
)

hospital_col = first_existing(
    df,
    ["Hospital_Name", "Hospital"]
)

hospital_type_col = first_existing(
    df,
    ["Hospital_Type", "Facility_Type"]
)

beds_col = first_existing(
    df,
    ["Total_Beds", "Beds", "Bed_Capacity"]
)

severity_col = first_existing(
    df,
    ["Severity_Level", "Severity"]
)

outcome_col = first_existing(
    df,
    ["Outcome"]
)

readmission_col = first_existing(
    df,
    ["Readmission_Flag", "Readmission_30_Days"]
)


# ---------------------------------------------------------
# CONVERT DATES
# ---------------------------------------------------------
if date_col:
    df[date_col] = pd.to_datetime(
        df[date_col],
        errors="coerce"
    )

if discharge_col:
    df[discharge_col] = pd.to_datetime(
        df[discharge_col],
        errors="coerce"
    )


# ---------------------------------------------------------
# NUMERIC CONVERSION
# ---------------------------------------------------------
for col in [wait_col, los_col, cost_col, beds_col]:
    if col:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔎 Filters")

filtered = df.copy()


# Admission date filter
if date_col and filtered[date_col].notna().any():

    min_date = filtered[date_col].min().date()
    max_date = filtered[date_col].max().date()

    date_range = st.sidebar.date_input(
        "Admission date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:

        filtered = filtered[
            (filtered[date_col].dt.date >= date_range[0]) &
            (filtered[date_col].dt.date <= date_range[1])
        ]


# Department filter
if dept_col:

    departments = sorted(
        filtered[dept_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_dept = st.sidebar.multiselect(
        "Department",
        departments,
        default=[]
    )

    if selected_dept:
        filtered = filtered[
            filtered[dept_col]
            .astype(str)
            .isin(selected_dept)
        ]


# Hospital type filter
if hospital_type_col:

    types = sorted(
        filtered[hospital_type_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_type = st.sidebar.multiselect(
        "Hospital Type",
        types,
        default=[]
    )

    if selected_type:
        filtered = filtered[
            filtered[hospital_type_col]
            .astype(str)
            .isin(selected_type)
        ]


# Diagnosis filter
if diagnosis_col:

    diagnoses = sorted(
        filtered[diagnosis_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_diagnosis = st.sidebar.multiselect(
        "Diagnosis",
        diagnoses,
        default=[]
    )

    if selected_diagnosis:
        filtered = filtered[
            filtered[diagnosis_col]
            .astype(str)
            .isin(selected_diagnosis)
        ]


# Severity filter
if severity_col:

    severities = sorted(
        filtered[severity_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_severity = st.sidebar.multiselect(
        "Severity",
        severities,
        default=[]
    )

    if selected_severity:
        filtered = filtered[
            filtered[severity_col]
            .astype(str)
            .isin(selected_severity)
        ]


st.sidebar.write(
    f"**Records after filters:** {len(filtered):,}"
)


if filtered.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------
page = st.sidebar.radio(
    "📌 Dashboard Section",
    [
        "Overview",
        "Patient Movement",
        "Treatment Facility",
        "Admission Trends",
        "Discharge Analysis",
        "Service Demand",
        "Treatment Workload",
        "Operational Bottlenecks",
        "Service Capacity"
    ]
)


# =========================================================
# OVERVIEW
# =========================================================
if page == "Overview":

    st.subheader("📊 Operational Overview")

    total_patients = (
        filtered[patient_col].nunique()
        if patient_col
        else len(filtered)
    )

    total_doctors = (
        filtered[doctor_id_col].nunique()
        if doctor_id_col
        else filtered[doctor_col].nunique()
        if doctor_col
        else 0
    )

    avg_wait = safe_mean(
        filtered,
        wait_col
    )

    avg_los = safe_mean(
        filtered,
        los_col
    )

    total_cost = (
        filtered[cost_col].sum()
        if cost_col
        else None
    )

    # KPI CARDS
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "👥 Patients",
        f"{total_patients:,}"
    )

    c2.metric(
        "👨‍⚕️ Doctors",
        f"{total_doctors:,}"
    )

    c3.metric(
        "⏱️ Avg Wait",
        f"{avg_wait:.1f} min"
        if avg_wait is not None
        else "N/A"
    )

    c4.metric(
        "🛏️ Avg LOS",
        f"{avg_los:.2f} days"
        if avg_los is not None
        else "N/A"
    )

    c5.metric(
        "💰 Treatment Cost",
        money(total_cost)
        if total_cost is not None
        else "N/A"
    )

    st.divider()

    # -----------------------------------------------------
    # OVERVIEW CHARTS 1 & 2
    # -----------------------------------------------------
    col1, col2 = st.columns(2)

    if dept_col:

        dept = (
            filtered[dept_col]
            .value_counts()
            .reset_index()
        )

        dept.columns = [
            "Department",
            "Patients"
        ]

        fig = px.bar(
            dept,
            x="Department",
            y="Patients",
            color="Patients",
            title="Patients by Department"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if diagnosis_col:

        diag = (
            filtered[diagnosis_col]
            .value_counts()
            .reset_index()
        )

        diag.columns = [
            "Diagnosis",
            "Patients"
        ]

        fig = px.pie(
            diag,
            names="Diagnosis",
            values="Patients",
            hole=0.45,
            title="Diagnosis Distribution"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # NEW OVERVIEW CHART 3
    # -----------------------------------------------------
    col1, col2 = st.columns(2)

    if outcome_col:

        outcome_status = (
            filtered[outcome_col]
            .astype(str)
            .str.strip()
            .str.title()
        )

        outcome_summary = (
            outcome_status
            .value_counts()
            .reset_index()
        )

        outcome_summary.columns = [
            "Outcome",
            "Patients"
        ]

        fig = px.pie(
            outcome_summary,
            names="Outcome",
            values="Patients",
            hole=0.45,
            title="Patient Outcome Distribution"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # NEW OVERVIEW CHART 4
    # -----------------------------------------------------
    if dept_col and wait_col and los_col:

        overview_dept = (
            filtered.groupby(dept_col)
            .agg(
                Avg_Wait=(wait_col, "mean"),
                Avg_LOS=(los_col, "mean")
            )
            .reset_index()
        )

        overview_long = overview_dept.melt(
            id_vars=dept_col,
            value_vars=[
                "Avg_Wait",
                "Avg_LOS"
            ],
            var_name="Metric",
            value_name="Average"
        )

        overview_long["Metric"] = (
            overview_long["Metric"]
            .map({
                "Avg_Wait": "Average Wait (min)",
                "Avg_LOS": "Average LOS (days)"
            })
        )

        fig = px.bar(
            overview_long,
            x=dept_col,
            y="Average",
            color="Metric",
            barmode="group",
            title="Average Wait Time & Length of Stay by Department"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# PATIENT MOVEMENT
# =========================================================
elif page == "Patient Movement":

    st.subheader(
        "👥 Patient Movement Analysis"
    )

    # -----------------------------------------------------
    # DEPARTMENT PATIENT COUNT
    # -----------------------------------------------------
    if dept_col:

        dept = (
            filtered[dept_col]
            .value_counts()
            .reset_index()
        )

        dept.columns = [
            "Department",
            "Patients"
        ]

        fig = px.bar(
            dept.sort_values("Patients"),
            x="Patients",
            y="Department",
            orientation="h",
            color="Patients",
            title="Department-wise Patient Count"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # WAIT TIME & LOS
    # -----------------------------------------------------
    col1, col2 = st.columns(2)

    if wait_col and dept_col:

        wait = (
            filtered.groupby(dept_col)[wait_col]
            .mean()
            .reset_index()
            .sort_values(
                wait_col,
                ascending=False
            )
        )

        fig = px.bar(
            wait,
            x=dept_col,
            y=wait_col,
            color=wait_col,
            title="Average Waiting Time by Department",
            labels={
                wait_col:
                "Average Wait (minutes)"
            }
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if los_col and dept_col:

        los = (
            filtered.groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(
                los_col,
                ascending=False
            )
        )

        fig = px.bar(
            los,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Length of Stay by Department"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # DIAGNOSIS BY DEPARTMENT
    # -----------------------------------------------------
    if diagnosis_col and dept_col:

        cross = (
            filtered
            .groupby(
                [dept_col, diagnosis_col]
            )
            .size()
            .reset_index(
                name="Patients"
            )
        )

        fig = px.bar(
            cross,
            x=dept_col,
            y="Patients",
            color=diagnosis_col,
            barmode="stack",
            title="Diagnosis Distribution by Department"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # PATIENT OUTCOME STATUS
    # =====================================================
    if outcome_col:

        st.divider()

        st.subheader(
            "❤️ Patient Outcome Status"
        )

        # Clean outcome values
        outcome_status = (
            filtered[outcome_col]
            .astype(str)
            .str.strip()
            .str.title()
        )

        # Count each outcome
        outcome_summary = (
            outcome_status
            .value_counts()
            .reset_index()
        )

        outcome_summary.columns = [
            "Outcome",
            "Patients"
        ]

        # Keep required outcomes
        required_outcomes = [
            "Recovered",
            "Improved",
            "Transferred"
        ]

        outcome_summary = (
            outcome_summary[
                outcome_summary["Outcome"]
                .isin(required_outcomes)
            ]
            .copy()
        )

        # Make sure all three categories appear
        for outcome in required_outcomes:

            if outcome not in outcome_summary["Outcome"].values:

                outcome_summary = pd.concat(
                    [
                        outcome_summary,
                        pd.DataFrame({
                            "Outcome": [outcome],
                            "Patients": [0]
                        })
                    ],
                    ignore_index=True
                )

        # Correct order
        outcome_summary["Outcome"] = pd.Categorical(
            outcome_summary["Outcome"],
            categories=required_outcomes,
            ordered=True
        )

        outcome_summary = (
            outcome_summary
            .sort_values("Outcome")
        )

        # -------------------------------------------------
        # KPI CARDS
        # -------------------------------------------------
        recovered = int(
            outcome_summary.loc[
                outcome_summary["Outcome"]
                == "Recovered",
                "Patients"
            ].sum()
        )

        improved = int(
            outcome_summary.loc[
                outcome_summary["Outcome"]
                == "Improved",
                "Patients"
            ].sum()
        )

        transferred = int(
            outcome_summary.loc[
                outcome_summary["Outcome"]
                == "Transferred",
                "Patients"
            ].sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "✅ Recovered",
            f"{recovered:,}"
        )

        c2.metric(
            "📈 Improved",
            f"{improved:,}"
        )

        c3.metric(
            "🔄 Transferred",
            f"{transferred:,}"
        )

        # -------------------------------------------------
        # OUTCOME CHARTS
        # -------------------------------------------------
        col1, col2 = st.columns(2)

        # Bar chart
        fig = px.bar(
            outcome_summary,
            x="Outcome",
            y="Patients",
            text="Patients",
            color="Outcome",
            title="Patients by Outcome"
        )

        fig.update_traces(
            textposition="outside"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

        # Pie chart
        fig = px.pie(
            outcome_summary,
            names="Outcome",
            values="Patients",
            hole=0.45,
            title="Patient Outcome Distribution"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

        # -------------------------------------------------
        # RECOVERY RATE BY DEPARTMENT
        # -------------------------------------------------
        if dept_col:

            movement_recovery = pd.DataFrame({
                dept_col:
                    filtered[dept_col],
                "Outcome":
                    outcome_status
            })

            recovery_dept = (
                movement_recovery
                .groupby(dept_col)
                .agg(
                    Total_Patients=(
                        "Outcome",
                        "size"
                    ),
                    Recovered=(
                        "Outcome",
                        lambda x:
                        (x == "Recovered").sum()
                    ),
                    Improved=(
                        "Outcome",
                        lambda x:
                        (x == "Improved").sum()
                    ),
                    Transferred=(
                        "Outcome",
                        lambda x:
                        (x == "Transferred").sum()
                    )
                )
                .reset_index()
            )

            recovery_dept["Recovery Rate (%)"] = (
                (
                    recovery_dept["Recovered"]
                    +
                    recovery_dept["Improved"]
                )
                /
                recovery_dept["Total_Patients"]
                * 100
            )

            fig = px.bar(
                recovery_dept.sort_values(
                    "Recovery Rate (%)"
                ),
                x=dept_col,
                y="Recovery Rate (%)",
                color="Recovery Rate (%)",
                text="Recovery Rate (%)",
                title="Recovery / Improvement Rate by Department"
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# =========================================================
# TREATMENT FACILITY
# =========================================================
elif page == "Treatment Facility":

    st.subheader(
        "🏥 Treatment Facility Analysis"
    )

    col1, col2 = st.columns(2)

    if hospital_col:

        hospital = (
            filtered[hospital_col]
            .value_counts()
            .reset_index()
            .head(15)
        )

        hospital.columns = [
            "Hospital",
            "Patients"
        ]

        fig = px.bar(
            hospital.sort_values("Patients"),
            x="Patients",
            y="Hospital",
            orientation="h",
            color="Patients",
            title="Top Hospitals by Patient Volume"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if hospital_type_col:

        facility = (
            filtered[hospital_type_col]
            .value_counts()
            .reset_index()
        )

        facility.columns = [
            "Hospital Type",
            "Patients"
        ]

        fig = px.pie(
            facility,
            names="Hospital Type",
            values="Patients",
            hole=0.45,
            title="Government vs Private"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    if dept_col and cost_col:

        cost = (
            filtered.groupby(dept_col)[cost_col]
            .mean()
            .reset_index()
            .sort_values(
                cost_col,
                ascending=False
            )
        )

        fig = px.bar(
            cost,
            x=dept_col,
            y=cost_col,
            color=cost_col,
            title="Average Treatment Cost by Department"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if dept_col and los_col:

        stay = (
            filtered.groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(
                los_col,
                ascending=False
            )
        )

        fig = px.bar(
            stay,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Stay by Department"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    if beds_col:

        avg_beds = filtered[beds_col].mean()

        st.metric(
            "🛏️ Average Facility Bed Capacity",
            f"{avg_beds:,.0f}"
        )


# =========================================================
# ADMISSION TRENDS
# =========================================================
elif page == "Admission Trends":

    st.subheader(
        "📅 Admission Trend Analysis"
    )

    if not date_col:

        st.warning(
            "No admission date column was found."
        )

        st.stop()

    daily = (
        filtered
        .dropna(subset=[date_col])
        .groupby(
            filtered[date_col].dt.date
        )
        .size()
        .reset_index(
            name="Admissions"
        )
    )

    daily.columns = [
        "Date",
        "Admissions"
    ]

    monthly = (
        filtered
        .dropna(subset=[date_col])
        .assign(
            Month=
            filtered[date_col]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("Month")
        .size()
        .reset_index(
            name="Admissions"
        )
    )

    col1, col2 = st.columns(2)

    fig = px.line(
        daily,
        x="Date",
        y="Admissions",
        markers=True,
        title="Daily Admissions"
    )

    col1.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.line(
        monthly,
        x="Month",
        y="Admissions",
        markers=True,
        title="Monthly Admissions"
    )

    col2.plotly_chart(
        fig,
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    peak = daily.nlargest(
        10,
        "Admissions"
    )

    fig = px.bar(
        peak.sort_values("Admissions"),
        x="Admissions",
        y="Date",
        orientation="h",
        color="Admissions",
        title="Top 10 Peak Admission Days"
    )

    col1.plotly_chart(
        fig,
        use_container_width=True
    )

    weekday = (
        filtered[date_col]
        .dt.day_name()
        .value_counts()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ],
            fill_value=0
        )
        .reset_index()
    )

    weekday.columns = [
        "Day",
        "Admissions"
    ]

    fig = px.bar(
        weekday,
        x="Day",
        y="Admissions",
        color="Admissions",
        title="Admissions by Day of Week"
    )

    col2.plotly_chart(
        fig,
        use_container_width=True
    )

    if len(monthly) > 1:

        monthly["Growth %"] = (
            monthly["Admissions"]
            .pct_change()
            * 100
        )

        fig = px.bar(
            monthly,
            x="Month",
            y="Growth %",
            title="Month-over-Month Admission Growth (%)",
            text="Growth %"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# DISCHARGE ANALYSIS
# =========================================================
elif page == "Discharge Analysis":

    st.subheader(
        "🚪 Discharge Rate Analysis"
    )

    if not outcome_col or not dept_col:

        st.warning(
            "Outcome and Department columns are required."
        )

        st.stop()

    successful = (
        filtered[outcome_col]
        .astype(str)
        .str.strip()
        .str.title()
        .isin([
            "Recovered",
            "Improved"
        ])
    )

    total = len(filtered)

    discharged = int(
        successful.sum()
    )

    rate = (
        discharged /
        total *
        100
        if total
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Patients",
        f"{total:,}"
    )

    c2.metric(
        "Successful Discharges",
        f"{discharged:,}"
    )

    c3.metric(
        "Overall Discharge Rate",
        f"{rate:.1f}%"
    )

    if date_col:

        temp = (
            filtered
            .dropna(subset=[date_col])
            .copy()
        )

        temp["Month"] = (
            temp[date_col]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            temp
            .groupby(
                ["Month", outcome_col]
            )
            .size()
            .reset_index(
                name="Patients"
            )
        )

        fig = px.line(
            monthly,
            x="Month",
            y="Patients",
            color=outcome_col,
            markers=True,
            title="Monthly Patient Outcome Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    total_dept = (
        filtered
        .groupby(dept_col)
        .size()
        .reset_index(
            name="Total Patients"
        )
    )

    good_dept = (
        filtered[successful]
        .groupby(dept_col)
        .size()
        .reset_index(
            name="Discharged Patients"
        )
    )

    dr = (
        total_dept
        .merge(
            good_dept,
            on=dept_col,
            how="left"
        )
        .fillna({
            "Discharged Patients": 0
        })
    )

    dr["Discharge Rate (%)"] = (
        dr["Discharged Patients"] /
        dr["Total Patients"] *
        100
    )

    col1, col2 = st.columns(2)

    fig = px.bar(
        dr.sort_values(
            "Discharge Rate (%)"
        ),
        x=dept_col,
        y="Discharge Rate (%)",
        color="Discharge Rate (%)",
        title="Discharge Rate by Department"
    )

    col1.plotly_chart(
        fig,
        use_container_width=True
    )

    if los_col:

        avg_stay = (
            filtered
            .groupby(dept_col)[los_col]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            avg_stay.sort_values(los_col),
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Length of Stay by Department",
            labels={
                los_col:
                "Average LOS (Days)"
            }
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    fig = px.bar(
        dr.sort_values(
            "Discharge Rate (%)"
        ),
        x=dept_col,
        y="Discharge Rate (%)",
        color="Discharge Rate (%)",
        title="Discharge Efficiency by Department"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# SERVICE DEMAND
# =========================================================
elif page == "Service Demand":

    st.subheader(
        "📈 Service Demand Analysis"
    )

    if dept_col:

        dept_demand = (
            filtered
            .groupby(dept_col)
            .size()
            .reset_index(
                name="Patients"
            )
            .sort_values(
                "Patients",
                ascending=False
            )
        )

        fig = px.bar(
            dept_demand,
            x=dept_col,
            y="Patients",
            text="Patients",
            color=dept_col,
            title="Patient Admissions by Department"
        )

        fig.update_traces(
            textposition="outside"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    if diagnosis_col:

        diag = (
            filtered
            .groupby(diagnosis_col)
            .size()
            .reset_index(
                name="Patients"
            )
            .sort_values(
                "Patients",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            diag,
            x=diagnosis_col,
            y="Patients",
            text="Patients",
            color="Patients",
            title="Top 10 Diagnoses by Patient Demand"
        )

        fig.update_traces(
            textposition="outside"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if dept_col and cost_col:

        costs = (
            filtered
            .groupby(dept_col)[cost_col]
            .agg(
                Average_Cost="mean",
                Total_Cost="sum",
                Patients="count"
            )
            .reset_index()
            .sort_values(
                "Total_Cost",
                ascending=False
            )
        )

        fig = px.bar(
            costs,
            x=dept_col,
            y="Total_Cost",
            text_auto=".2s",
            color=dept_col,
            title="Treatment Cost by Department"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    if date_col:

        temp = (
            filtered
            .dropna(subset=[date_col])
            .copy()
        )

        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        temp["Month"] = (
            temp[date_col]
            .dt.month_name()
        )

        monthly = (
            temp
            .groupby("Month")
            .size()
            .reset_index(
                name="Patients"
            )
        )

        monthly["Month"] = pd.Categorical(
            monthly["Month"],
            categories=month_order,
            ordered=True
        )

        monthly = monthly.sort_values(
            "Month"
        )

        col1, col2 = st.columns(2)

        fig = px.line(
            monthly,
            x="Month",
            y="Patients",
            markers=True,
            title="Monthly Service Demand"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

        temp["Weekday"] = (
            temp[date_col]
            .dt.day_name()
        )

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        weekday = (
            temp
            .groupby("Weekday")
            .size()
            .reset_index(
                name="Patients"
            )
        )

        weekday["Weekday"] = pd.Categorical(
            weekday["Weekday"],
            categories=days,
            ordered=True
        )

        weekday = weekday.sort_values(
            "Weekday"
        )

        fig = px.bar(
            weekday,
            x="Weekday",
            y="Patients",
            text="Patients",
            color="Patients",
            title="Patient Admissions by Weekday"
        )

        fig.update_traces(
            textposition="outside"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    admission_time = first_existing(
        filtered,
        [
            "Admission_Time",
            "Admission Time"
        ]
    )

    if admission_time:

        temp = filtered.copy()

        temp["_time"] = pd.to_datetime(
            temp[admission_time],
            errors="coerce"
        )

        temp["_hour"] = (
            temp["_time"].dt.hour
        )

        hourly = (
            temp
            .dropna(subset=["_hour"])
            .groupby("_hour")
            .size()
            .reset_index(
                name="Patients"
            )
        )

        hourly["Time"] = (
            hourly["_hour"]
            .astype(int)
            .map(
                lambda x:
                f"{x:02d}:00"
            )
        )

        fig = px.line(
            hourly,
            x="Time",
            y="Patients",
            markers=True,
            title="Patient Admissions by Hour"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# TREATMENT WORKLOAD
# =========================================================
elif page == "Treatment Workload":

    st.subheader(
        "👨‍⚕️ Treatment Workload Analysis"
    )

    total_patients = (
        filtered[patient_col].nunique()
        if patient_col
        else len(filtered)
    )

    total_doctors = (
        filtered[doctor_id_col].nunique()
        if doctor_id_col
        else filtered[doctor_col].nunique()
        if doctor_col
        else 0
    )

    ratio = (
        total_patients /
        total_doctors
        if total_doctors
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Patients",
        f"{total_patients:,}"
    )

    c2.metric(
        "Doctors",
        f"{total_doctors:,}"
    )

    c3.metric(
        "Patient / Doctor Ratio",
        f"{ratio:.2f}"
        if ratio
        else "N/A"
    )

    col1, col2 = st.columns(2)

    if doctor_col:

        doctor = (
            filtered
            .groupby(doctor_col)
            .agg(
                Patients=(
                    patient_col,
                    "count"
                )
                if patient_col
                else (
                    doctor_col,
                    "size"
                )
            )
            .reset_index()
            .sort_values(
                "Patients",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            doctor.sort_values("Patients"),
            x="Patients",
            y=doctor_col,
            orientation="h",
            color="Patients",
            title="Top 10 Busiest Doctors"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if dept_col:

        workload = (
            filtered
            .groupby(dept_col)
            .size()
            .reset_index(
                name="Patients"
            )
            .sort_values(
                "Patients",
                ascending=False
            )
        )

        fig = px.bar(
            workload,
            x=dept_col,
            y="Patients",
            color="Patients",
            title="Department Workload"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

    col1, col2 = st.columns(2)

    if diagnosis_col:

        treatment = (
            filtered[diagnosis_col]
            .value_counts()
            .reset_index()
        )

        treatment.columns = [
            "Diagnosis",
            "Patients"
        ]

        fig = px.bar(
            treatment,
            x="Diagnosis",
            y="Patients",
            color="Patients",
            title="Treatment Volume by Diagnosis"
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

    if dept_col and los_col:

        duration = (
            filtered
            .groupby(dept_col)[los_col]
            .mean()
            .reset_index()
            .sort_values(
                los_col,
                ascending=False
            )
        )

        fig = px.bar(
            duration,
            x=dept_col,
            y=los_col,
            color=los_col,
            title="Average Treatment Duration"
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# OPERATIONAL BOTTLENECKS
# =========================================================
elif page == "Operational Bottlenecks":

    st.subheader(
        "⚠️ Operational Bottleneck Analysis"
    )

    if wait_col:

        avg_wait = (
            filtered[wait_col].mean()
        )

        over_3hr = (
            filtered[wait_col] > 180
        ).mean() * 100

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Wait",
            f"{avg_wait:.1f} min"
        )

        c2.metric(
            "Waiting > 3 Hours",
            f"{over_3hr:.1f}%"
        )

        if los_col:

            c3.metric(
                "Average LOS",
                f"{filtered[los_col].mean():.2f} days"
            )

        if dept_col:

            wait_dept = (
                filtered
                .groupby(dept_col)[wait_col]
                .mean()
                .reset_index()
                .sort_values(
                    wait_col,
                    ascending=False
                )
            )

            fig = px.bar(
                wait_dept,
                x=dept_col,
                y=wait_col,
                color=wait_col,
                title="Average Wait Time by Department"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Wait-time categories
        bins = [
            0,
            60,
            120,
            180,
            240,
            300,
            float("inf")
        ]

        labels = [
            "<1 hr",
            "1-2 hr",
            "2-3 hr",
            "3-4 hr",
            "4-5 hr",
            "5+ hr"
        ]

        temp = filtered.copy()

        temp["Wait_Category"] = pd.cut(
            temp[wait_col],
            bins=bins,
            labels=labels,
            include_lowest=True
        )

        queue = (
            temp["Wait_Category"]
            .value_counts()
            .reindex(
                labels,
                fill_value=0
            )
            .reset_index()
        )

        queue.columns = [
            "Wait Category",
            "Patients"
        ]

        fig = px.bar(
            queue,
            x="Wait Category",
            y="Patients",
            color="Patients",
            title="Waiting-Time Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if los_col and severity_col:

        expected_los = (
            filtered[severity_col]
            .map({
                "Low": 2,
                "Medium": 5,
                "High": 14,
                "Critical": 21
            })
        )

        delay = (
            filtered[los_col] -
            expected_los
        ).clip(lower=0)

        delay_df = pd.DataFrame({
            "Severity":
                filtered[severity_col],
            "Discharge Delay":
                delay
        })

        delay_df = (
            delay_df
            .groupby("Severity")[
                "Discharge Delay"
            ]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            delay_df,
            x="Severity",
            y="Discharge Delay",
            color="Discharge Delay",
            title="Average Discharge Delay by Severity",
            labels={
                "Discharge Delay":
                "Delay (days)"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if readmission_col:

        readmission = (
            filtered[readmission_col]
        )

        if readmission.dtype == object:

            readmission = (
                readmission
                .astype(str)
                .str.lower()
                .isin([
                    "1",
                    "yes",
                    "true",
                    "readmitted"
                ])
                .astype(int)
            )

        else:

            readmission = (
                pd.to_numeric(
                    readmission,
                    errors="coerce"
                )
                .fillna(0)
            )

        st.metric(
            "Readmission Rate",
            f"{readmission.mean() * 100:.2f}%"
        )


# =========================================================
# SERVICE CAPACITY
# =========================================================
elif page == "Service Capacity":

    st.subheader(
        "🛏️ Service Capacity Analysis"
    )

    st.caption(
        "Capacity metrics follow the methodology from the team's "
        "Service Capacity Analysis: bed occupancy, staffing workload, "
        "department utilization, critical-patient risk, monthly capacity "
        "trends, and hospital performance scorecard."
    )

    if (
        not hospital_col
        or not beds_col
        or not patient_col
    ):

        st.warning(
            "Service Capacity requires Hospital_Name, "
            "Total_Beds and Patient_ID columns."
        )

        st.stop()

    # -----------------------------------------------------
    # BED OCCUPANCY
    # -----------------------------------------------------
    hospital_beds = (
        filtered
        .groupby(
            [
                hospital_col,
                hospital_type_col
            ]
            if hospital_type_col
            else [hospital_col]
        )
        .agg(
            Patient_Count=(
                patient_col,
                "count"
            ),
            Total_Beds=(
                beds_col,
                "first"
            )
        )
        .reset_index()
    )

    hospital_beds["Occupancy_Rate"] = (
        hospital_beds["Patient_Count"] /
        hospital_beds["Total_Beds"]
        .replace(0, pd.NA)
    ) * 100

    hospital_beds = (
        hospital_beds
        .dropna(
            subset=["Occupancy_Rate"]
        )
        .sort_values(
            "Occupancy_Rate",
            ascending=False
        )
    )

    avg_occupancy = (
        hospital_beds["Occupancy_Rate"].mean()
        if not hospital_beds.empty
        else 0
    )

    over_85 = int(
        (
            hospital_beds["Occupancy_Rate"]
            > 85
        ).sum()
    )

    under_70 = int(
        (
            hospital_beds["Occupancy_Rate"]
            < 70
        ).sum()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Average Occupancy",
        f"{avg_occupancy:.1f}%"
    )

    c2.metric(
        "Hospitals > 85%",
        f"{over_85}"
    )

    c3.metric(
        "Hospitals < 70%",
        f"{under_70}"
    )

    if not hospital_beds.empty:

        fig = px.bar(
            hospital_beds,
            x=hospital_col,
            y="Occupancy_Rate",
            color="Occupancy_Rate",
            text="Occupancy_Rate",
            title="Hospital Bed Occupancy Rate",
            labels={
                "Occupancy_Rate":
                "Occupancy %",
                hospital_col:
                "Hospital"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig.add_hline(
            y=85,
            line_dash="dash",
            annotation_text="Critical Level (85%)"
        )

        fig.add_hline(
            y=70,
            line_dash="dash",
            annotation_text="Warning Level (70%)"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.info(
            "Hospitals operating above 85% occupancy are treated "
            "as critical-capacity facilities; hospitals below 70% "
            "have comparatively more available capacity."
        )

    # -----------------------------------------------------
    # STAFFING WORKLOAD
    # -----------------------------------------------------
    st.subheader(
        "👨‍⚕️ Staffing Workload"
    )

    if (
        dept_col
        and doctor_id_col
        and nurse_id_col
    ):

        staffing = (
            filtered
            .groupby(
                [
                    hospital_col,
                    dept_col
                ]
            )
            .agg(
                Patient_Count=(
                    patient_col,
                    "count"
                ),
                Doctors=(
                    doctor_id_col,
                    "nunique"
                ),
                Nurses=(
                    nurse_id_col,
                    "nunique"
                )
            )
            .reset_index()
        )

        staffing["Patients_per_Doctor"] = (
            staffing["Patient_Count"] /
            staffing["Doctors"]
            .replace(0, pd.NA)
        )

        staffing["Patients_per_Nurse"] = (
            staffing["Patient_Count"] /
            staffing["Nurses"]
            .replace(0, pd.NA)
        )

        staffing = (
            staffing
            .sort_values(
                "Patient_Count",
                ascending=False
            )
            .head(10)
        )

        col1, col2 = st.columns(2)

        fig = px.bar(
            staffing
            .sort_values(
                "Patients_per_Doctor"
            ),
            x=dept_col,
            y="Patients_per_Doctor",
            color="Patients_per_Doctor",
            title="Patients per Doctor — Top 10 Departments",
            labels={
                "Patients_per_Doctor":
                "Patients per Doctor"
            }
        )

        fig.add_hline(
            y=15,
            line_dash="dash",
            annotation_text="Doctor reference (15:1)"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        col1.plotly_chart(
            fig,
            use_container_width=True
        )

        fig = px.bar(
            staffing
            .sort_values(
                "Patients_per_Nurse"
            ),
            x=dept_col,
            y="Patients_per_Nurse",
            color="Patients_per_Nurse",
            title="Patients per Nurse — Top 10 Departments",
            labels={
                "Patients_per_Nurse":
                "Patients per Nurse"
            }
        )

        fig.add_hline(
            y=10,
            line_dash="dash",
            annotation_text="Nurse reference (10:1)"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        col2.plotly_chart(
            fig,
            use_container_width=True
        )

        st.info(
            "Departments above 15 patients per doctor "
            "or above 10 patients per nurse are flagged "
            "for staffing attention."
        )

    elif dept_col and doctor_id_col:

        st.warning(
            "Nurse_ID is not available, so only the "
            "patient-to-doctor workload is shown."
        )

        staffing = (
            filtered
            .groupby(
                [
                    hospital_col,
                    dept_col
                ]
            )
            .agg(
                Patient_Count=(
                    patient_col,
                    "count"
                ),
                Doctors=(
                    doctor_id_col,
                    "nunique"
                )
            )
            .reset_index()
        )

        staffing["Patients_per_Doctor"] = (
            staffing["Patient_Count"] /
            staffing["Doctors"]
            .replace(0, pd.NA)
        )

        staffing = (
            staffing
            .sort_values(
                "Patient_Count",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            staffing
            .sort_values(
                "Patients_per_Doctor"
            ),
            x=dept_col,
            y="Patients_per_Doctor",
            color="Patients_per_Doctor",
            title="Patients per Doctor — Top 10 Departments"
        )

        fig.add_hline(
            y=15,
            line_dash="dash",
            annotation_text="Doctor reference (15:1)"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.warning(
            "Doctor_ID and/or Nurse_ID columns are not available."
        )

    # -----------------------------------------------------
    # DEPARTMENT-WISE UTILIZATION HEATMAP
    # -----------------------------------------------------
    if dept_col and not hospital_beds.empty:

        st.subheader(
            "🏥 Department-Wise Bed Utilization"
        )

        dept_util = (
            filtered
            .groupby(
                [
                    hospital_col,
                    dept_col
                ]
            )
            .agg(
                Patient_Count=(
                    patient_col,
                    "count"
                ),
                Total_Beds=(
                    beds_col,
                    "first"
                )
            )
            .reset_index()
        )

        dept_util["Utilization"] = (
            dept_util["Patient_Count"] /
            dept_util["Total_Beds"]
            .replace(0, pd.NA)
        ) * 100

        heatmap_data = (
            dept_util
            .pivot_table(
                values="Utilization",
                index=hospital_col,
                columns=dept_col,
                fill_value=0
            )
        )

        if not heatmap_data.empty:

            fig = px.imshow(
                heatmap_data,
                text_auto=".1f",
                aspect="auto",
                title="Department-Wise Bed Utilization Heatmap",
                labels={
                    "color": "Utilization %",
                    "x": "Department",
                    "y": "Hospital"
                }
            )

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------------------------------
    # CRITICAL PATIENT CAPACITY RISK
    # -----------------------------------------------------
    if severity_col:

        st.subheader(
            "🚨 Critical Patient Capacity Risk"
        )

        critical_levels = [
            "Critical",
            "High",
            "Medium"
        ]

        critical_data = filtered[
            filtered[severity_col]
            .isin(critical_levels)
        ].copy()

        critical_summary = (
            critical_data
            .groupby(
                [
                    hospital_col,
                    severity_col
                ]
            )
            .agg(
                Patient_Count=(
                    patient_col,
                    "count"
                )
            )
            .reset_index()
        )

        critical_summary = (
            critical_summary
            .pivot_table(
                values="Patient_Count",
                index=hospital_col,
                columns=severity_col,
                fill_value=0
            )
            .reset_index()
        )

        for level in critical_levels:

            if level not in critical_summary.columns:

                critical_summary[level] = 0

        bed_info = (
            filtered
            .groupby(hospital_col)[beds_col]
            .first()
            .reset_index()
        )

        critical_summary = (
            critical_summary
            .merge(
                bed_info,
                on=hospital_col,
                how="left"
            )
        )

        critical_summary["Total_Critical"] = (
            critical_summary["Critical"] +
            critical_summary["High"] +
            critical_summary["Medium"]
        )

        critical_summary["Risk_Score"] = (
            critical_summary["Total_Critical"] /
            critical_summary[beds_col]
            .replace(0, pd.NA)
        ) * 100

        critical_summary = (
            critical_summary
            .dropna(
                subset=["Risk_Score"]
            )
            .sort_values(
                "Risk_Score",
                ascending=False
            )
            .head(10)
        )

        if not critical_summary.empty:

            fig = px.bar(
                critical_summary,
                x=hospital_col,
                y="Risk_Score",
                color="Risk_Score",
                text="Risk_Score",
                title="Critical Patient Capacity Risk Score",
                labels={
                    "Risk_Score":
                    "Critical Patient Risk %"
                }
            )

            fig.update_traces(
                texttemplate="%{text:.1f}%",
                textposition="outside"
            )

            fig.add_hline(
                y=20,
                line_dash="dash",
                annotation_text="High Risk (20%)"
            )

            fig.add_hline(
                y=10,
                line_dash="dash",
                annotation_text="Medium Risk (10%)"
            )

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------------------------------
    # MONTHLY CAPACITY TREND
    # -----------------------------------------------------
    if date_col:

        st.subheader(
            "📅 Monthly Capacity Trend"
        )

        monthly = (
            filtered
            .dropna(subset=[date_col])
            .copy()
        )

        monthly["Month"] = (
            monthly[date_col]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        monthly_trend = (
            monthly
            .groupby(
                [
                    "Month",
                    hospital_col
                ]
            )
            .agg(
                Patient_Count=(
                    patient_col,
                    "count"
                ),
                Total_Beds=(
                    beds_col,
                    "first"
                )
            )
            .reset_index()
        )

        monthly_trend["Occupancy"] = (
            monthly_trend["Patient_Count"] /
            monthly_trend["Total_Beds"]
            .replace(0, pd.NA)
        ) * 100

        fig = px.line(
            monthly_trend,
            x="Month",
            y="Occupancy",
            color=hospital_col,
            markers=True,
            title="Monthly Capacity Trends",
            labels={
                "Occupancy":
                "Occupancy %"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # HOSPITAL PERFORMANCE SCORECARD
    # -----------------------------------------------------
    if not hospital_beds.empty:

        st.subheader(
            "🏆 Hospital Performance Scorecard"
        )

        score_df = hospital_beds.copy()

        score_df["Score"] = (
            score_df["Occupancy_Rate"]
            .apply(
                lambda x:
                "A (Good)"
                if x < 70
                else
                "B (Moderate)"
                if x < 85
                else
                "C (Critical)"
            )
        )

        scorecard = (
            score_df
            .groupby("Score")[hospital_col]
            .count()
            .reset_index(
                name="Count"
            )
        )

        fig = px.pie(
            scorecard,
            values="Count",
            names="Score",
            hole=0.4,
            title="Hospital Performance Scorecard"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        critical_hospitals = (
            score_df[
                score_df["Score"]
                == "C (Critical)"
            ][hospital_col]
            .tolist()
        )

        if critical_hospitals:

            st.warning(
                "Critical-capacity hospitals: "
                +
                ", ".join(
                    map(
                        str,
                        critical_hospitals[:10]
                    )
                )
            )

        else:

            st.success(
                "No hospital is above the "
                "critical 85% occupancy threshold "
                "in the current filter."
            )


# =========================================================
# FOOTER

# =========================================================
st.divider()

st.caption(
    "Healthcare Operations Dashboard | "
    "Streamlit + Plotly | "
    "Interactive filters update all available charts."
)