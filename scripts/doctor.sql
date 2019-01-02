CREATE TABLE public.doctor
(
    doctor_id SERIAL NOT NULL,
    name character varying(50), 
    access integer NOT NULL,
    login character varying(20) NOT NULL, 
    password character varying(30) NOT NULL,   
    CONSTRAINT doctor_pkey PRIMARY KEY (doctor_id)
);
