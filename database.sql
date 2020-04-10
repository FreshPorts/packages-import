-- The tables are required are:

-- Table: public.abi

-- DROP TABLE public.abi;

CREATE TABLE public.abi
(
    id integer NOT NULL DEFAULT nextval('abi_id_seq'::regclass),
    name text COLLATE pg_catalog."default" NOT NULL,
    active boolean NOT NULL DEFAULT true,
    CONSTRAINT abi_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE public.abi
    OWNER to dan;

GRANT ALL ON TABLE public.abi TO dan;

GRANT SELECT ON TABLE public.abi TO packaging;

COMMENT ON TABLE public.abi
    IS 'list of ABI - e.g. FreeBSD:12:amd64';

COMMENT ON COLUMN public.abi.active
    IS 'Do we still fetch packages for this ABI';
    

insert into abi (name) values ('FreeBSD:12:amd64');


-- Table: public.packages_raw

-- DROP TABLE public.packages_raw;

CREATE TABLE public.packages_raw
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1 ),
    abi_id integer NOT NULL,
    package_origin text COLLATE pg_catalog."default" NOT NULL,
    package_name text COLLATE pg_catalog."default" NOT NULL,
    package_version text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT packages_raw_pkey PRIMARY KEY (id),
    CONSTRAINT packages_raw_abi_id_fk FOREIGN KEY (abi_id)
        REFERENCES public.abi (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)

TABLESPACE pg_default;

ALTER TABLE public.packages_raw
    OWNER to dan;

GRANT ALL ON TABLE public.packages_raw TO dan;

GRANT INSERT ON TABLE public.packages_raw TO packaging;
-- Index: fki_packages_raw_abi_id_fk

-- DROP INDEX public.fki_packages_raw_abi_id_fk;

CREATE INDEX fki_packages_raw_abi_id_fk
    ON public.packages_raw USING btree
    (abi_id ASC NULLS LAST)
    TABLESPACE pg_default;





