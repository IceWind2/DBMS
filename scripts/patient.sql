CREATE TABLE public.patient
(
    patient_id SERIAL NOT NULL,
    name character varying(40),
    sex character(1),
    birth_date character varying(15),
    ill_date character varying(15),
    diagnosis character varying(100) NOT NULL,
    address character varying(100),
    CONSTRAINT patient_pkey PRIMARY KEY (patient_id),
    CONSTRAINT entry_unq UNIQUE (name, birth_date)
);
