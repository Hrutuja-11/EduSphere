import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import CustomUser, StudentProfile, FacultyProfile, HODProfile, PlacementOfficerProfile
from academics.models import Department, Course, CourseEnrollment, AttendanceRecord, ExamResult
from portfolio.models import Skill, Project, Certification, Achievement, Endorsement
from placements.models import Company, JobPosting, JobApplication

class Command(BaseCommand):
    help = 'Seeds the database with test data for EduSphere.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting existing data...")
        JobApplication.objects.all().delete()
        JobPosting.objects.all().delete()
        Company.objects.all().delete()
        Endorsement.objects.all().delete()
        Project.objects.all().delete()
        Certification.objects.all().delete()
        Achievement.objects.all().delete()
        Skill.objects.all().delete()
        AttendanceRecord.objects.all().delete()
        ExamResult.objects.all().delete()
        CourseEnrollment.objects.all().delete()
        Course.objects.all().delete()
        Department.objects.all().delete()
        CustomUser.objects.exclude(is_superuser=True).delete()

        self.stdout.write("Creating skills...")
        skills_list = ["Python", "Django", "React", "PostgreSQL", "Machine Learning", "AWS", "Docker", "UI/UX Design", "Java", "C++", "SQL", "HTML/CSS"]
        skills_objs = {}
        for name in skills_list:
            s, _ = Skill.objects.get_or_create(name=name)
            skills_objs[name] = s

        self.stdout.write("Creating departments...")
        cse, _ = Department.objects.get_or_create(name="Computer Science & Engineering", code="CSE")
        ece, _ = Department.objects.get_or_create(name="Electronics & Communication Engineering", code="ECE")
        it, _ = Department.objects.get_or_create(name="Information Technology", code="IT")

        self.stdout.write("Creating courses...")
        # CSE Courses
        dbms = Course.objects.create(name="Database Management Systems", code="CS302", department=cse, credits=4, semester=5)
        dsa = Course.objects.create(name="Data Structures and Algorithms", code="CS201", department=cse, credits=4, semester=3)
        se = Course.objects.create(name="Software Engineering", code="CS401", department=cse, credits=3, semester=5)
        
        # ECE Courses
        mp = Course.objects.create(name="Microprocessors", code="EC301", department=ece, credits=4, semester=5)
        dsp = Course.objects.create(name="Digital Signal Processing", code="EC304", department=ece, credits=3, semester=5)

        self.stdout.write("Creating users...")
        # Faculty 1 (CSE)
        fac1_user = CustomUser.objects.create_user(username="faculty1", email="faculty1@edusphere.edu", password="password123", role="faculty", phone_number="9876543210")
        fac1_profile = fac1_user.faculty_profile
        fac1_profile.employee_id = "FAC-CSE-01"
        fac1_profile.department = cse
        fac1_profile.designation = "Assistant Professor"
        fac1_profile.save()

        # Faculty 2 (CSE)
        fac2_user = CustomUser.objects.create_user(username="faculty2", email="faculty2@edusphere.edu", password="password123", role="faculty", phone_number="9876543211")
        fac2_profile = fac2_user.faculty_profile
        fac2_profile.employee_id = "FAC-CSE-02"
        fac2_profile.department = cse
        fac2_profile.designation = "Associate Professor"
        fac2_profile.save()

        # HOD (CSE)
        hod_user = CustomUser.objects.create_user(username="hod1", email="hod1@edusphere.edu", password="password123", role="hod", phone_number="9876543220")
        hod_profile = hod_user.hod_profile
        hod_profile.department = cse
        hod_profile.department_managed = "Computer Science & Engineering"
        hod_profile.office_location = "Block A, Room 302"
        hod_profile.save()

        # Placement Officer
        po_user = CustomUser.objects.create_user(username="placement1", email="placement@edusphere.edu", password="password123", role="placement_officer", phone_number="9876543230")
        po_profile = po_user.placement_profile
        po_profile.office_contact = "+91 80 2345 6789"
        po_profile.save()

        # Student 1 (High CGPA - Eligible for Google/Microsoft)
        std1_user = CustomUser.objects.create_user(username="student1", email="student1@edusphere.edu", password="password123", role="student", phone_number="9900990099")
        std1_profile = std1_user.student_profile
        std1_profile.enrollment_number = "1RE22CS045"
        std1_profile.department = cse
        std1_profile.major = "Computer Science"
        std1_profile.current_semester = 5
        std1_profile.graduation_year = 2028
        std1_profile.cgpa = 8.90
        std1_profile.skills.add(skills_objs["Python"], skills_objs["Django"], skills_objs["React"], skills_objs["SQL"], skills_objs["HTML/CSS"])
        std1_profile.save()

        # Student 2 (Lower CGPA - Testing Placement Gate)
        std2_user = CustomUser.objects.create_user(username="student2", email="student2@edusphere.edu", password="password123", role="student", phone_number="9900990088")
        std2_profile = std2_user.student_profile
        std2_profile.enrollment_number = "1RE22CS082"
        std2_profile.department = cse
        std2_profile.major = "Computer Science"
        std2_profile.current_semester = 5
        std2_profile.graduation_year = 2028
        std2_profile.cgpa = 7.20
        std2_profile.skills.add(skills_objs["Java"], skills_objs["C++"], skills_objs["SQL"])
        std2_profile.save()

        self.stdout.write("Enrolling students and setting grades...")
        # Enroll Student 1
        se_enroll1 = CourseEnrollment.objects.create(student=std1_profile, course=se, semester=5, grade="A", attendance_percentage=94.50)
        dbms_enroll1 = CourseEnrollment.objects.create(student=std1_profile, course=dbms, semester=5, grade="A+", attendance_percentage=96.00)
        dsa_enroll1 = CourseEnrollment.objects.create(student=std1_profile, course=dsa, semester=3, grade="B+", attendance_percentage=88.20)

        # Enroll Student 2
        se_enroll2 = CourseEnrollment.objects.create(student=std2_profile, course=se, semester=5, grade="B", attendance_percentage=82.00)
        dbms_enroll2 = CourseEnrollment.objects.create(student=std2_profile, course=dbms, semester=5, grade="C", attendance_percentage=78.50)

        # Exam Results for Student 1 in DBMS
        ExamResult.objects.create(enrollment=dbms_enroll1, assessment_name="Internal-1", max_marks=25.00, marks_obtained=23.50)
        ExamResult.objects.create(enrollment=dbms_enroll1, assessment_name="Internal-2", max_marks=25.00, marks_obtained=24.00)
        ExamResult.objects.create(enrollment=dbms_enroll1, assessment_name="Semester End Exam", max_marks=100.00, marks_obtained=92.00)

        # Attendance Log sample for student 1 in DBMS
        today = timezone.now().date()
        for idx in range(10):
            d = today - datetime.timedelta(days=idx)
            AttendanceRecord.objects.create(enrollment=dbms_enroll1, date=d, status='present' if idx != 4 else 'absent')

        self.stdout.write("Creating projects, certifications and achievements...")
        # Student 1 Portfolio Items
        # Pending Project
        p_pending = Project.objects.create(
            student=std1_profile,
            title="EduSphere Academic Portal",
            description="An integrated student academic, portfolio and career management system built with Python, Django, and modern CSS. Features role-based dashboards, verified credentials, public shareable resumes, and eligibility gates.",
            technologies_used="Python, Django, SQLite, CSS, HTML5",
            project_link="https://github.com/student1/edusphere",
            git_repository="https://github.com/student1/edusphere",
            verification_status="pending"
        )
        # Verified Project
        p_verified = Project.objects.create(
            student=std1_profile,
            title="Smart Crop Health Analyzer",
            description="An IoT device coupled with a Machine Learning model that checks soil moisture, NPK levels, and crop leaf images to classify crop disease and suggest tailored fertilizer actions.",
            technologies_used="Python, TensorFlow, Raspberry Pi, React Native",
            project_link="https://github.com/student1/crop-analyzer",
            verification_status="verified",
            verified_by=fac1_profile,
            verification_date=timezone.now() - datetime.timedelta(days=10),
            faculty_comments="Excellent implementation of Deep Learning on microcontrollers. Validated working hardware prototype."
        )

        # Pending Certification
        c_pending = Certification.objects.create(
            student=std1_profile,
            name="AWS Certified Solutions Architect - Associate",
            issuing_organization="Amazon Web Services (AWS)",
            issue_date=timezone.now().date() - datetime.timedelta(days=60),
            credential_id="AWS-ASA-998877",
            credential_url="https://aws.amazon.com/verification",
            verification_status="pending"
        )
        # Verified Certification
        c_verified = Certification.objects.create(
            student=std1_profile,
            name="Google Professional Cloud Developer",
            issuing_organization="Google Cloud Platform (GCP)",
            issue_date=timezone.now().date() - datetime.timedelta(days=120),
            credential_id="GCP-PCD-112233",
            credential_url="https://gcp.com/verify/112233",
            verification_status="verified",
            verified_by=fac1_profile,
            verification_date=timezone.now() - datetime.timedelta(days=10),
            faculty_comments="Verified the official PDF credential from Google Cloud Portal."
        )

        # Pending Achievement
        a_pending = Achievement.objects.create(
            student=std1_profile,
            title="First Prize - National Hackathon 'HackCSE'",
            category="extracurricular",
            description="Won first place out of 150 teams across the country for designing and developing a real-time decentralized emergency response routing app in 36 hours.",
            date=timezone.now().date() - datetime.timedelta(days=30),
            verification_status="pending"
        )

        # Endorsement for Student 1
        Endorsement.objects.create(
            student=std1_profile,
            faculty=fac1_profile,
            relationship="project_guide",
            content="Student1 is a highly diligent student. They led their academic capstone project group with exceptional professionalism and demonstrated deep expertise in full-stack architecture. I highly recommend them for any senior backend or Django development roles."
        )

        self.stdout.write("Creating placement companies and job openings...")
        google = Company.objects.create(name="Google LLC", industry="Technology/Software", website="https://google.com", description="Google is a global leader in search, cloud, AI, and hardware services.")
        amazon = Company.objects.create(name="Amazon", industry="E-Commerce/Cloud", website="https://amazon.com", description="Amazon is a multinational tech company specializing in e-commerce, AWS, and retail.")
        microsoft = Company.objects.create(name="Microsoft", industry="Enterprise Software", website="https://microsoft.com", description="Microsoft is a pioneer in operating systems, Azure cloud, and enterprise computing.")
        tcs = Company.objects.create(name="Tata Consultancy Services", industry="IT Services", website="https://tcs.com", description="TCS is a global IT consulting and business services organization.")

        # Job 1: Google Intern (CGPA gate: 8.00)
        g_intern = JobPosting.objects.create(
            company=google,
            title="Software Engineering Intern",
            description="Join Google's Core Infrastructure team for a 3-month summer internship. Work on high-performance API architectures and scale services that serve billions of queries per day.",
            requirements="Solid grasp of Python, Go or C++, understanding of Data Structures & Algorithms, web protocols.",
            location="Bangalore (Hybrid)",
            job_type="internship",
            salary_range="1,00,000 INR/Month",
            min_cgpa=8.00,
            application_deadline=timezone.now().date() + datetime.timedelta(days=45),
            is_active=True
        )

        # Job 2: Amazon Data Analyst (CGPA gate: 7.50)
        a_analyst = JobPosting.objects.create(
            company=amazon,
            title="Business Data Analyst",
            description="Analyze customer metrics, build interactive Tableau/QuickSight dashboards, and write highly optimized SQL queries to assist product managers in key business decisions.",
            requirements="SQL proficiency, Python (pandas, numpy), data visualization, analytical reasoning.",
            location="Hyderabad (On-site)",
            job_type="full_time",
            salary_range="15,00,000 INR/Year",
            min_cgpa=7.50,
            application_deadline=timezone.now().date() + datetime.timedelta(days=30),
            is_active=True
        )

        # Job 3: Microsoft Software Engineer (CGPA gate: 8.50)
        m_swe = JobPosting.objects.create(
            company=microsoft,
            title="Software Engineer - Cloud & Edge",
            description="Build next-generation services on Microsoft Azure. Focus on distributed computing, virtualization architectures, and high-availability systems.",
            requirements="Proficiency in C#, Java or C++, experience with cloud platforms, multi-threaded programming.",
            location="Noida (Remote)",
            job_type="full_time",
            salary_range="24,00,000 INR/Year",
            min_cgpa=8.50,
            application_deadline=timezone.now().date() + datetime.timedelta(days=15),
            is_active=True
        )

        # Job 4: TCS Systems Engineer (CGPA gate: 6.00)
        tcs_se = JobPosting.objects.create(
            company=tcs,
            title="Systems Engineer Trainee",
            description="Entry level engineering program. You will be trained in enterprise systems development and deployed on large scale financial/retail project teams.",
            requirements="Basic coding understanding in Java, Python or C++, general engineering degree.",
            location="Pune (On-site)",
            job_type="full_time",
            salary_range="4,50,000 INR/Year",
            min_cgpa=6.00,
            application_deadline=timezone.now().date() + datetime.timedelta(days=90),
            is_active=True
        )

        self.stdout.write("Submitting sample applications...")
        # Student 1 applies to Google (eligible)
        JobApplication.objects.create(
            job_posting=g_intern,
            student=std1_profile,
            resume_url="https://edusphere.edu/portfolio/student1/",
            status="applied"
        )
        
        # Student 1 applies to Amazon (eligible)
        JobApplication.objects.create(
            job_posting=a_analyst,
            student=std1_profile,
            resume_url="https://edusphere.edu/portfolio/student1/",
            status="shortlisted",
            placement_officer_comments="Student meets the requirements and projects showcase strong data handling. Shortlisted for interview round."
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded EduSphere data!"))
